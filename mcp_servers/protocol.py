"""MCP protocol data models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MCPMessageType(str, Enum):
    """MCP message types."""

    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"
    TOOL_LIST = "tool_list"
    TOOL_REGISTRATION = "tool_registration"
    HEARTBEAT = "heartbeat"
    SHUTDOWN = "shutdown"


class MCPToolParameter(BaseModel):
    """MCP tool parameter definition."""

    name: str
    description: str
    type: str
    required: bool = True
    default: Any | None = None
    enum: list[Any] | None = None


class MCPToolDefinition(BaseModel):
    """MCP tool definition."""

    name: str
    description: str
    parameters: list[MCPToolParameter]
    examples: list[dict[str, Any]] | None = None
    category: str | None = None
    tags: list[str] | None = None


class MCPToolCall(BaseModel):
    """MCP tool call message."""

    message_type: MCPMessageType = MCPMessageType.TOOL_CALL
    tool_name: str
    parameters: dict[str, Any]
    call_id: str = Field(default_factory=lambda: datetime.now().isoformat())
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPToolResult(BaseModel):
    """MCP tool result message."""

    message_type: MCPMessageType = MCPMessageType.TOOL_RESULT
    call_id: str
    result: Any
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPToolError(BaseModel):
    """MCP tool error message."""

    message_type: MCPMessageType = MCPMessageType.TOOL_ERROR
    call_id: str
    error_type: str
    error_message: str
    stack_trace: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPToolList(BaseModel):
    """MCP tool list message."""

    message_type: MCPMessageType = MCPMessageType.TOOL_LIST
    tools: list[MCPToolDefinition]
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPToolRegistration(BaseModel):
    """MCP tool registration message."""

    message_type: MCPMessageType = MCPMessageType.TOOL_REGISTRATION
    tool: MCPToolDefinition
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPHeartbeat(BaseModel):
    """MCP heartbeat message."""

    message_type: MCPMessageType = MCPMessageType.HEARTBEAT
    server_id: str
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPShutdown(BaseModel):
    """MCP shutdown message."""

    message_type: MCPMessageType = MCPMessageType.SHUTDOWN
    reason: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Union type for all MCP messages
MCPMessage = MCPToolCall | MCPToolResult | MCPToolError | MCPToolList | MCPToolRegistration | MCPHeartbeat | MCPShutdown


def validate_mcp_message(data: dict[str, Any]) -> MCPMessage:
    """Validate and parse an MCP message.

    Args:
        data: The message data to validate.

    Returns:
        The validated message as the appropriate type.

    Raises:
        ValueError: If the message is invalid or has an unknown type.
    """
    if "message_type" not in data:
        raise ValueError("Message missing required field 'message_type'")

    message_type = data["message_type"]

    if message_type == MCPMessageType.TOOL_CALL:
        return MCPToolCall(**data)
    elif message_type == MCPMessageType.TOOL_RESULT:
        return MCPToolResult(**data)
    elif message_type == MCPMessageType.TOOL_ERROR:
        return MCPToolError(**data)
    elif message_type == MCPMessageType.TOOL_LIST:
        return MCPToolList(**data)
    elif message_type == MCPMessageType.TOOL_REGISTRATION:
        return MCPToolRegistration(**data)
    elif message_type == MCPMessageType.HEARTBEAT:
        return MCPHeartbeat(**data)
    elif message_type == MCPMessageType.SHUTDOWN:
        return MCPShutdown(**data)
    else:
        raise ValueError(f"Unknown message type: {message_type}")


def serialize_mcp_message(message: MCPMessage) -> dict[str, Any]:
    """Serialize an MCP message to a dictionary.

    Args:
        message: The message to serialize.

    Returns:
        The serialized message as a dictionary.
    """
    # Use mode='json' to ensure datetime objects are serialized as ISO strings
    return message.model_dump(mode="json")
