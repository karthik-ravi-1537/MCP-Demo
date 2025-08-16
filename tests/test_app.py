"""Tests for the FastAPI application."""

from fastapi.testclient import TestClient

from server.app import app


client = TestClient(app)


def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MCP Demo Project" in response.text


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()


def test_api_docs():
    """Test the API docs endpoint."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_not_found():
    """Test 404 error handling."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "The requested resource was not found."