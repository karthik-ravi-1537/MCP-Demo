"""Base class for MCP servers."""

import asyncio
import inspect
import json
import logging
import traceback
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import websockets
from websockets.server import WebSocketServerProtocol

from .protocol import (
    MCPToolCall,
    MCPToolDefinition,
    MCPToolError,
    MCPToolList,
    MCPToolParameter,
    MCPToolResult,
    serialize_mcp_message,
    validate_mcp_message,
)

# Type variable for tool functions
T = TypeVar("T")


def tool(
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to mark a method as an MCP tool.

    Args:
        name: Name of the tool. If not provided, uses the function name.
        description: Description of the tool. If not provided, uses the function docstring.
        category: Category of the tool.
        tags: Tags for the tool.

    Returns:
        Decorated function.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        func._mcp_tool = True  # type: ignore
        func._mcp_tool_name = name or func.__name__  # type: ignore
        func._mcp_tool_description = description or func.__doc__ or ""  # type: ignore
        func._mcp_tool_category = category  # type: ignore
        func._mcp_tool_tags = tags or []  # type: ignore

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BaseMCPServer(ABC):
    """Base class for all MCP servers in the demo project."""

    def __init__(
        self,
        name: str,
        description: str,
        host: str = "localhost",
        port: int = 5000,
        log_level: int = logging.INFO,
    ):
        """Initialize the MCP server.

        Args:
            name: Name of the server.
            description: Description of the server.
            host: Host to bind to.
            port: Port to bind to.
            log_level: Logging level.
        """
        self.name = name
        self.description = description
        self.host = host
        self.port = port

        # Set up logging
        self.logger = logging.getLogger(f"mcp.servers.{self.name}")
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Tool registry
        self.tools: dict[str, Callable] = {}
        self.tool_definitions: dict[str, MCPToolDefinition] = {}

        # Active connections
        self.active_connections: set[WebSocketServerProtocol] = set()

        # Register tools from methods decorated with @tool
        self._register_decorated_tools()

    def _register_decorated_tools(self) -> None:
        """Register all methods decorated with @tool."""
        for _name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, "_mcp_tool") and method._mcp_tool:
                tool_name = method._mcp_tool_name
                tool_description = method._mcp_tool_description
                tool_category = method._mcp_tool_category
                tool_tags = method._mcp_tool_tags

                self.register_tool(
                    tool_name,
                    method,
                    tool_description,
                    category=tool_category,
                    tags=tool_tags,
                )

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Register a tool with the server.

        Args:
            name: Name of the tool.
            func: Function implementing the tool.
            description: Description of the tool. If not provided, uses the function docstring.
            category: Category of the tool.
            tags: Tags for the tool.
        """
        if name in self.tools:
            self.logger.warning(f"Tool {name} already registered, overwriting")

        self.tools[name] = func

        # Extract parameter information from function signature
        sig = inspect.signature(func)
        parameters = []

        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter for methods
            if param_name == "self":
                continue

            # Determine parameter type
            param_type = "any"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict or param.annotation == dict:
                    param_type = "object"

            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty

            # Get default value if any
            default = None if param.default == inspect.Parameter.empty else param.default

            # Create parameter definition
            parameters.append(
                MCPToolParameter(
                    name=param_name,
                    description=f"Parameter {param_name}",  # Default description
                    type=param_type,
                    required=required,
                    default=default,
                )
            )

        # Create tool definition
        self.tool_definitions[name] = MCPToolDefinition(
            name=name,
            description=description or func.__doc__ or "",
            parameters=parameters,
            category=category,
            tags=tags or [],
        )

        self.logger.info(f"Registered tool: {name}")

    async def handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Handle a WebSocket connection.

        Args:
            websocket: The WebSocket connection.
        """
        self.active_connections.add(websocket)
        self.logger.info(f"New connection from {websocket.remote_address}")

        try:
            # Send tool list on connection
            await self.send_tool_list(websocket)

            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    mcp_message = validate_mcp_message(data)

                    if isinstance(mcp_message, MCPToolCall):
                        await self.handle_tool_call(websocket, mcp_message)
                    else:
                        self.logger.warning(f"Unsupported message type: {mcp_message.message_type}")

                except json.JSONDecodeError:
                    self.logger.error("Invalid JSON message")

                except Exception as e:
                    self.logger.error(f"Error handling message: {e}")
                    traceback.print_exc()

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Connection closed: {websocket.remote_address}")

        finally:
            self.active_connections.remove(websocket)

    async def send_tool_list(self, websocket: WebSocketServerProtocol) -> None:
        """Send the list of available tools to a client.

        Args:
            websocket: The WebSocket connection.
        """
        tool_list = MCPToolList(tools=list(self.tool_definitions.values()))
        await websocket.send(json.dumps(serialize_mcp_message(tool_list)))

    async def handle_tool_call(self, websocket: WebSocketServerProtocol, call: MCPToolCall) -> None:
        """Handle a tool call.

        Args:
            websocket: The WebSocket connection.
            call: The tool call message.
        """
        self.logger.info(f"Tool call: {call.tool_name}")

        if call.tool_name not in self.tools:
            error = MCPToolError(
                call_id=call.call_id,
                error_type="ToolNotFoundError",
                error_message=f"Tool not found: {call.tool_name}",
            )
            await websocket.send(json.dumps(serialize_mcp_message(error)))
            return

        try:
            # Get the tool function
            tool_func = self.tools[call.tool_name]

            # Call the tool function with the provided parameters
            result = tool_func(**call.parameters)

            # If the result is a coroutine, await it
            if inspect.iscoroutine(result):
                result = await result

            # Send the result
            tool_result = MCPToolResult(call_id=call.call_id, result=result)
            await websocket.send(json.dumps(serialize_mcp_message(tool_result)))

        except Exception as e:
            # Send error message
            error = MCPToolError(
                call_id=call.call_id,
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            await websocket.send(json.dumps(serialize_mcp_message(error)))

    async def start_server(self) -> None:
        """Start the WebSocket server."""
        self.logger.info(f"Starting {self.name} on {self.host}:{self.port}")

        async with websockets.serve(self.handle_connection, self.host, self.port):
            # Keep the server running
            await asyncio.Future()

    def run(self) -> None:
        """Run the server (blocking)."""
        asyncio.run(self.start_server())

    @abstractmethod
    def get_tutorial_content(self) -> str:
        """Get tutorial content for this server.

        Returns:
            Markdown-formatted tutorial content explaining this server.
        """
        pass

    @abstractmethod
    def get_example_code(self) -> dict[str, str]:
        """Get example code for this server.

        Returns:
            Dictionary mapping example names to code snippets.
        """
        pass
