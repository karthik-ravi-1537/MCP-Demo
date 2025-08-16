"""Tests for the MCP server management API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from mcp_servers.base import BaseMCPServer
from server.app import app


client = TestClient(app)


class MockServer(BaseMCPServer):
    """Mock MCP server for testing."""
    
    def __init__(self):
        """Initialize the mock server."""
        self.tools = {
            "test_tool": self.test_tool,
        }
        self.tool_descriptions = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": [
                    {
                        "name": "param1",
                        "description": "Parameter 1",
                        "type": "string",
                        "required": True,
                    },
                ],
            },
        ]
    
    def test_tool(self, param1: str) -> str:
        """Test tool implementation."""
        if param1 == "error":
            raise ValueError("Test error")
        return f"Result: {param1}"
    
    def get_tutorial_content(self) -> str:
        """Get tutorial content."""
        return "# Mock Server Tutorial"
    
    def get_example_code(self) -> dict:
        """Get example code."""
        return {
            "example1": "server.test_tool('test')",
        }
    
    def get_tool_descriptions(self) -> list:
        """Get tool descriptions."""
        return self.tool_descriptions


@pytest.fixture
def mock_server_types():
    """Mock SERVER_TYPES dictionary."""
    return {
        "mock": MockServer,
    }


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_servers(mock_create_server):
    """Test getting all servers."""
    response = client.get("/api/servers/servers")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "mock"
    assert response.json()[0]["name"] == "MockServer"
    assert "health" in response.json()[0]


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_server(mock_create_server):
    """Test getting a server by ID."""
    response = client.get("/api/servers/servers/mock")
    assert response.status_code == 200
    assert response.json()["id"] == "mock"
    assert response.json()["name"] == "MockServer"
    assert "health" in response.json()


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
def test_get_server_not_found():
    """Test getting a non-existent server."""
    response = client.get("/api/servers/servers/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "The requested resource was not found."


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_server_health(mock_create_server):
    """Test getting server health."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    response = client.get("/api/servers/servers/mock/health")
    assert response.status_code == 200
    assert "status" in response.json()


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_check_server_health(mock_create_server):
    """Test checking server health."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    response = client.post("/api/servers/servers/mock/health/check")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "tool_count" in response.json()["details"]
    assert response.json()["details"]["tool_count"] == 1


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_server_tutorial(mock_create_server):
    """Test getting server tutorial content."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    response = client.get("/api/servers/servers/mock/tutorial")
    assert response.status_code == 200
    assert response.text == '"# Mock Server Tutorial"'


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_server_examples(mock_create_server):
    """Test getting server example code."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    response = client.get("/api/servers/servers/mock/examples")
    assert response.status_code == 200
    assert "example1" in response.json()
    assert response.json()["example1"] == "server.test_tool('test')"


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_get_server_tools(mock_create_server):
    """Test getting server tools."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    response = client.get("/api/servers/servers/mock/tools")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "test_tool"
    assert response.json()[0]["description"] == "A test tool"
    assert len(response.json()[0]["parameters"]) == 1
    assert response.json()[0]["parameters"][0]["name"] == "param1"


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_call_tool(mock_create_server):
    """Test calling a tool."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )
    
    response = client.post(
        "/api/servers/servers/mock/tools/test_tool",
        json={
            "tool_name": "test_tool",
            "parameters": {"param1": "test"},
            "call_id": "test-call",
        },
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert response.json()["call_id"] == "test-call"
    assert response.json()["result"] == "Result: test"


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_call_tool_not_found(mock_create_server):
    """Test calling a non-existent tool."""
    mock_server = MockServer()
    mock_create_server.return_value = mock_server
    
    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )
    
    response = client.post(
        "/api/servers/servers/mock/tools/nonexistent",
        json={
            "tool_name": "nonexistent",
            "parameters": {},
            "call_id": "test-call",
        },
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "The requested resource was not found."


@patch("server.api.mcp_servers.SERVER_TYPES", {"mock": MockServer})
@patch("server.api.mcp_servers.create_server")
def test_call_tool_error(mock_create_server):
    """Test calling a tool that raises an error."""
    mock_server = MockServer()
    mock_server.test_tool = MagicMock(side_effect=ValueError("Test error"))
    mock_create_server.return_value = mock_server
    
    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )
    
    response = client.post(
        "/api/servers/servers/mock/tools/test_tool",
        json={
            "tool_name": "test_tool",
            "parameters": {"param1": "error"},
            "call_id": "test-call",
        },
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Test error"