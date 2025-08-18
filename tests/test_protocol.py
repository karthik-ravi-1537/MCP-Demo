"""Tests for MCP protocol data models."""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from mcp_servers.protocol import (
    MCPMessageType,
    MCPToolCall,
    MCPToolDefinition,
    MCPToolError,
    MCPToolList,
    MCPToolParameter,
    MCPToolResult,
    serialize_mcp_message,
    validate_mcp_message,
)


def test_tool_parameter():
    """Test MCPToolParameter model."""
    param = MCPToolParameter(
        name="filename",
        description="Name of the file to read",
        type="string",
        required=True,
    )

    assert param.name == "filename"
    assert param.description == "Name of the file to read"
    assert param.type == "string"
    assert param.required is True
    assert param.default is None
    assert param.enum is None


def test_tool_definition():
    """Test MCPToolDefinition model."""
    tool = MCPToolDefinition(
        name="read_file",
        description="Read a file from the filesystem",
        parameters=[
            MCPToolParameter(
                name="filename",
                description="Name of the file to read",
                type="string",
                required=True,
            ),
            MCPToolParameter(
                name="encoding",
                description="File encoding",
                type="string",
                required=False,
                default="utf-8",
            ),
        ],
        category="filesystem",
        tags=["file", "io", "read"],
    )

    assert tool.name == "read_file"
    assert tool.description == "Read a file from the filesystem"
    assert len(tool.parameters) == 2
    assert tool.parameters[0].name == "filename"
    assert tool.parameters[1].name == "encoding"
    assert tool.category == "filesystem"
    assert "file" in tool.tags
    assert "io" in tool.tags
    assert "read" in tool.tags


def test_tool_call():
    """Test MCPToolCall model."""
    call = MCPToolCall(
        tool_name="read_file",
        parameters={"filename": "example.txt", "encoding": "utf-8"},
        call_id="123",
    )

    assert call.message_type == MCPMessageType.TOOL_CALL
    assert call.tool_name == "read_file"
    assert call.parameters["filename"] == "example.txt"
    assert call.parameters["encoding"] == "utf-8"
    assert call.call_id == "123"
    assert isinstance(call.timestamp, datetime)


def test_tool_result():
    """Test MCPToolResult model."""
    result = MCPToolResult(
        call_id="123",
        result="File content goes here",
    )

    assert result.message_type == MCPMessageType.TOOL_RESULT
    assert result.call_id == "123"
    assert result.result == "File content goes here"
    assert isinstance(result.timestamp, datetime)


def test_tool_error():
    """Test MCPToolError model."""
    error = MCPToolError(
        call_id="123",
        error_type="FileNotFoundError",
        error_message="File not found: example.txt",
        stack_trace="Traceback (most recent call last):\\n...",
    )

    assert error.message_type == MCPMessageType.TOOL_ERROR
    assert error.call_id == "123"
    assert error.error_type == "FileNotFoundError"
    assert error.error_message == "File not found: example.txt"
    assert error.stack_trace == "Traceback (most recent call last):\\n..."
    assert isinstance(error.timestamp, datetime)


def test_tool_list():
    """Test MCPToolList model."""
    tool_list = MCPToolList(
        tools=[
            MCPToolDefinition(
                name="read_file",
                description="Read a file from the filesystem",
                parameters=[
                    MCPToolParameter(
                        name="filename",
                        description="Name of the file to read",
                        type="string",
                        required=True,
                    ),
                ],
            ),
            MCPToolDefinition(
                name="write_file",
                description="Write to a file in the filesystem",
                parameters=[
                    MCPToolParameter(
                        name="filename",
                        description="Name of the file to write",
                        type="string",
                        required=True,
                    ),
                    MCPToolParameter(
                        name="content",
                        description="Content to write",
                        type="string",
                        required=True,
                    ),
                ],
            ),
        ],
    )

    assert tool_list.message_type == MCPMessageType.TOOL_LIST
    assert len(tool_list.tools) == 2
    assert tool_list.tools[0].name == "read_file"
    assert tool_list.tools[1].name == "write_file"
    assert isinstance(tool_list.timestamp, datetime)


def test_validate_mcp_message():
    """Test validate_mcp_message function."""
    # Test valid tool call
    data = {
        "message_type": "tool_call",
        "tool_name": "read_file",
        "parameters": {"filename": "example.txt"},
        "call_id": "123",
    }

    message = validate_mcp_message(data)
    assert isinstance(message, MCPToolCall)
    assert message.tool_name == "read_file"

    # Test valid tool result
    data = {
        "message_type": "tool_result",
        "call_id": "123",
        "result": "File content",
    }

    message = validate_mcp_message(data)
    assert isinstance(message, MCPToolResult)
    assert message.result == "File content"

    # Test invalid message (missing required field)
    data = {
        "message_type": "tool_call",
        # Missing tool_name
        "parameters": {"filename": "example.txt"},
        "call_id": "123",
    }

    with pytest.raises(ValidationError):
        validate_mcp_message(data)

    # Test invalid message (unknown message type)
    data = {
        "message_type": "unknown_type",
        "some_field": "some_value",
    }

    with pytest.raises(ValueError, match="Unknown message type"):
        validate_mcp_message(data)

    # Test invalid message (missing message_type)
    data = {
        "tool_name": "read_file",
        "parameters": {"filename": "example.txt"},
    }

    with pytest.raises(ValueError, match="Message missing required field"):
        validate_mcp_message(data)


def test_serialize_mcp_message():
    """Test serialize_mcp_message function."""
    call = MCPToolCall(
        tool_name="read_file",
        parameters={"filename": "example.txt"},
        call_id="123",
    )

    serialized = serialize_mcp_message(call)
    assert isinstance(serialized, dict)
    assert serialized["message_type"] == "tool_call"
    assert serialized["tool_name"] == "read_file"
    assert serialized["parameters"]["filename"] == "example.txt"
    assert serialized["call_id"] == "123"
    assert "timestamp" in serialized

    # Test that the serialized message can be converted to JSON
    json_str = json.dumps(serialized)
    assert isinstance(json_str, str)

    # Test that the serialized message can be parsed back
    parsed = json.loads(json_str)
    assert parsed["message_type"] == "tool_call"
    assert parsed["tool_name"] == "read_file"
