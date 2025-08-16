"""Tests for the base MCP server class."""

import asyncio
import json
import pytest
import websockets
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_servers.base import BaseMCPServer, tool
from mcp_servers.protocol import MCPToolCall, MCPToolResult, serialize_mcp_message


class TestServer(BaseMCPServer):
    """Test MCP server implementation."""
    
    def __init__(self, **kwargs):
        """Initialize the test server."""
        super().__init__(name="test_server", description="Test server", **kwargs)
    
    @tool(description="Add two numbers")
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    @tool(description="Concatenate two strings")
    def concat(self, a: str, b: str) -> str:
        """Concatenate two strings."""
        return a + b
    
    @tool(name="custom_name", description="Tool with custom name")
    def some_method(self, value: str) -> str:
        """Method with custom tool name."""
        return f"Custom: {value}"
    
    @tool(description="Async tool", category="async", tags=["async", "test"])
    async def async_tool(self, value: str) -> str:
        """Async tool example."""
        await asyncio.sleep(0.1)
        return f"Async: {value}"
    
    def get_tutorial_content(self) -> str:
        """Get tutorial content."""
        return "# Test Server\n\nThis is a test server."
    
    def get_example_code(self) -> dict:
        """Get example code."""
        return {
            "basic": "server = TestServer()\nresult = server.add(1, 2)",
        }


@pytest.fixture
def server():
    """Create a test server."""
    return TestServer()


def test_server_initialization(server):
    """Test server initialization."""
    assert server.name == "test_server"
    assert server.description == "Test server"
    assert server.host == "localhost"
    assert server.port == 5000
    
    # Check that tools were registered
    assert "add" in server.tools
    assert "concat" in server.tools
    assert "custom_name" in server.tools
    assert "async_tool" in server.tools
    
    # Check tool definitions
    assert "add" in server.tool_definitions
    assert server.tool_definitions["add"].description == "Add two numbers"
    assert len(server.tool_definitions["add"].parameters) == 2
    assert server.tool_definitions["add"].parameters[0].name == "a"
    assert server.tool_definitions["add"].parameters[0].type == "integer"
    
    assert "custom_name" in server.tool_definitions
    assert server.tool_definitions["custom_name"].description == "Tool with custom name"
    
    assert "async_tool" in server.tool_definitions
    assert server.tool_definitions["async_tool"].category == "async"
    assert "async" in server.tool_definitions["async_tool"].tags
    assert "test" in server.tool_definitions["async_tool"].tags


def test_tool_execution(server):
    """Test direct tool execution."""
    assert server.add(1, 2) == 3
    assert server.concat("hello", "world") == "helloworld"
    assert server.some_method("test") == "Custom: test"


@pytest.mark.asyncio
async def test_async_tool_execution(server):
    """Test async tool execution."""
    result = await server.async_tool("test")
    assert result == "Async: test"


@pytest.mark.asyncio
async def test_handle_tool_call():
    """Test handling a tool call."""
    server = TestServer()
    websocket = AsyncMock()
    
    # Create a tool call
    call = MCPToolCall(
        tool_name="add",
        parameters={"a": 1, "b": 2},
        call_id="test_call",
    )
    
    # Handle the call
    await server.handle_tool_call(websocket, call)
    
    # Check that the result was sent
    websocket.send.assert_called_once()
    sent_data = json.loads(websocket.send.call_args[0][0])
    assert sent_data["message_type"] == "tool_result"
    assert sent_data["call_id"] == "test_call"
    assert sent_data["result"] == 3


@pytest.mark.asyncio
async def test_handle_tool_call_error():
    """Test handling a tool call that raises an error."""
    server = TestServer()
    websocket = AsyncMock()
    
    # Create a tool call with invalid parameters
    call = MCPToolCall(
        tool_name="add",
        parameters={"a": "not_a_number", "b": 2},  # This will cause a TypeError
        call_id="test_call",
    )
    
    # Handle the call
    await server.handle_tool_call(websocket, call)
    
    # Check that an error was sent
    websocket.send.assert_called_once()
    sent_data = json.loads(websocket.send.call_args[0][0])
    assert sent_data["message_type"] == "tool_error"
    assert sent_data["call_id"] == "test_call"
    assert sent_data["error_type"] == "TypeError"


@pytest.mark.asyncio
async def test_handle_tool_call_not_found():
    """Test handling a call to a non-existent tool."""
    server = TestServer()
    websocket = AsyncMock()
    
    # Create a tool call for a non-existent tool
    call = MCPToolCall(
        tool_name="non_existent_tool",
        parameters={},
        call_id="test_call",
    )
    
    # Handle the call
    await server.handle_tool_call(websocket, call)
    
    # Check that an error was sent
    websocket.send.assert_called_once()
    sent_data = json.loads(websocket.send.call_args[0][0])
    assert sent_data["message_type"] == "tool_error"
    assert sent_data["call_id"] == "test_call"
    assert sent_data["error_type"] == "ToolNotFoundError"


@pytest.mark.asyncio
async def test_send_tool_list():
    """Test sending the tool list."""
    server = TestServer()
    websocket = AsyncMock()
    
    # Send the tool list
    await server.send_tool_list(websocket)
    
    # Check that the tool list was sent
    websocket.send.assert_called_once()
    sent_data = json.loads(websocket.send.call_args[0][0])
    assert sent_data["message_type"] == "tool_list"
    assert len(sent_data["tools"]) == 4  # add, concat, custom_name, async_tool