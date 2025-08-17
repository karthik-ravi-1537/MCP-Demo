"""API endpoints for MCP servers."""

import asyncio
import logging
import time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from mcp_servers import SERVER_TYPES, create_server
from mcp_servers.protocol import MCPToolCall

from .sessions import SessionData, get_active_session

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Server health status
server_health: dict[str, dict] = {}


class ToolCallRequest(BaseModel):
    """Tool call request model."""

    tool_name: str
    parameters: dict
    call_id: str


class ServerStartRequest(BaseModel):
    """Server start request model."""

    host: str = "localhost"
    port: int = 5000


def update_server_health(server_id: str, status: str, details: dict | None = None) -> None:
    """Update server health status.

    Args:
        server_id: ID of the server.
        status: Status of the server.
        details: Optional details about the status.
    """
    server_health[server_id] = {
        "status": status,
        "last_updated": time.time(),
        "details": details or {},
    }


async def check_server_health(server_id: str) -> None:
    """Check server health in the background.

    Args:
        server_id: ID of the server.
    """
    try:
        # Create the server
        server = create_server(server_id)

        # Get the tool descriptions
        tools = server.get_tool_descriptions()

        # Update health status
        update_server_health(
            server_id,
            "healthy",
            {
                "tool_count": len(tools),
                "tools": [tool["name"] for tool in tools],
            },
        )

    except Exception as e:
        # Update health status with error
        update_server_health(
            server_id,
            "error",
            {
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )


@router.get("/servers", response_model=list[dict])
async def get_servers():
    """Get all available MCP servers."""
    return [
        {
            "id": server_id,
            "name": server_class.__name__,
            "description": server_class.__doc__ or "",
            "health": server_health.get(server_id, {"status": "unknown"}),
        }
        for server_id, server_class in SERVER_TYPES.items()
    ]


@router.get("/servers/{server_id}", response_model=dict)
async def get_server(
    server_id: str = Path(..., description="ID of the server to get"),
    background_tasks: BackgroundTasks = None,
):
    """Get an MCP server by ID."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    server_class = SERVER_TYPES[server_id]

    # Check server health in the background
    if background_tasks is not None:
        background_tasks.add_task(check_server_health, server_id)

    return {
        "id": server_id,
        "name": server_class.__name__,
        "description": server_class.__doc__ or "",
        "health": server_health.get(server_id, {"status": "unknown"}),
    }


@router.get("/servers/{server_id}/health", response_model=dict)
async def get_server_health(
    server_id: str = Path(..., description="ID of the server to get"),
    background_tasks: BackgroundTasks = None,
):
    """Get health status for an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    # Check server health in the background
    if background_tasks is not None:
        background_tasks.add_task(check_server_health, server_id)

    return server_health.get(server_id, {"status": "unknown"})


@router.post("/servers/{server_id}/health/check", response_model=dict)
async def check_server_health_endpoint(
    server_id: str = Path(..., description="ID of the server to check"),
):
    """Check health status for an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    # Check server health
    await check_server_health(server_id)

    return server_health.get(server_id, {"status": "unknown"})


@router.get("/servers/{server_id}/tutorial", response_model=str)
async def get_server_tutorial(server_id: str = Path(..., description="ID of the server to get")):
    """Get tutorial content for an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    server = create_server(server_id)

    return server.get_tutorial_content()


@router.get("/servers/{server_id}/examples", response_model=dict[str, str])
async def get_server_examples(server_id: str = Path(..., description="ID of the server to get")):
    """Get example code for an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    server = create_server(server_id)

    return server.get_example_code()


@router.get("/servers/{server_id}/tools", response_model=list[dict])
async def get_server_tools(server_id: str = Path(..., description="ID of the server to get")):
    """Get tools provided by an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    server = create_server(server_id)

    return server.get_tool_descriptions()


@router.post("/servers/{server_id}/tools/{tool_name}", response_model=dict)
async def call_tool(
    request: ToolCallRequest,
    server_id: str = Path(..., description="ID of the server"),
    tool_name: str = Path(..., description="Name of the tool to call"),
    session: SessionData = Depends(get_active_session),
):
    """Call a tool on an MCP server."""
    if server_id not in SERVER_TYPES:
        raise HTTPException(status_code=404, detail="Server not found")

    server = create_server(server_id)

    if tool_name not in server.tools:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

    try:
        # Call the tool
        result = server.tools[tool_name](**request.parameters)

        # If the result is a coroutine, await it
        if asyncio.iscoroutine(result):
            result = await result

        return {
            "call_id": request.call_id,
            "result": result,
        }

    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.websocket("/ws/{server_id}")
async def websocket_endpoint(websocket: WebSocket, server_id: str):
    """WebSocket endpoint for MCP servers."""
    if server_id not in SERVER_TYPES:
        await websocket.close(code=1008, reason="Server not found")
        return

    server = create_server(server_id)

    await websocket.accept()

    try:
        # Send the list of available tools
        tools = server.get_tool_descriptions()
        await websocket.send_json(
            {
                "message_type": "tool_list",
                "tools": tools,
            }
        )

        # Handle messages
        async for message in websocket.iter_json():
            try:
                if message.get("message_type") == "tool_call":
                    # Create a tool call
                    tool_call = MCPToolCall(
                        tool_name=message["tool_name"],
                        parameters=message["parameters"],
                        call_id=message.get("call_id", ""),
                    )

                    # Call the tool
                    await server.handle_tool_call(websocket, tool_call)

                else:
                    # Send an error for unsupported message types
                    await websocket.send_json(
                        {
                            "message_type": "error",
                            "error": f"Unsupported message type: {message.get('message_type')}",
                        }
                    )

            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json(
                    {
                        "message_type": "error",
                        "error": str(e),
                    }
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {server_id}")

    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
        await websocket.close(code=1011, reason=str(e))
