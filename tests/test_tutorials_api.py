"""Tests for the tutorial API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.app import app
from tutorials.models import (
    CodeExample,
    DifficultyLevel,
    Exercise,
    Tutorial,
    TutorialSection,
)

client = TestClient(app)


@pytest.fixture
def mock_tutorial():
    """Create a mock tutorial."""
    return Tutorial(
        id="test-tutorial",
        title="Test Tutorial",
        description="A tutorial for testing",
        level=DifficultyLevel.BEGINNER,
        prerequisites=[],
        estimated_time=30,
        sections=[
            TutorialSection(
                id="section-1",
                title="Section 1",
                content="This is section 1",
                code_examples=[
                    CodeExample(
                        id="example-1",
                        title="Example 1",
                        description="This is example 1",
                        code="print('Hello, world!')",
                        language="python",
                    ),
                ],
                exercises=[
                    Exercise(
                        id="exercise-1",
                        title="Exercise 1",
                        description="This is exercise 1",
                        difficulty=DifficultyLevel.BEGINNER,
                        starter_code="# Write your code here",
                        solution_code="print('Solution')",
                        test_cases=[],
                        hints=[],
                        max_attempts=3,
                    ),
                ],
            ),
        ],
    )


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "session_id" in response.json()
    assert response.json()["username"] == "testuser"

    # Check that a session cookie was set
    assert "session_id" in response.cookies


def test_login_user():
    """Test user login."""
    response = client.post(
        "/api/tutorials/users/login",
        json={"username": "testuser"},
    )
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "session_id" in response.json()
    assert response.json()["username"] == "testuser"

    # Check that a session cookie was set
    assert "session_id" in response.cookies


def test_get_current_user_unauthorized():
    """Test getting the current user without a session."""
    response = client.get("/api/tutorials/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_current_user():
    """Test getting the current user with a session."""
    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )

    # Get the current user
    response = client.get(
        "/api/tutorials/users/me",
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "last_active" in response.json()


@patch("tutorials.list_tutorials")
def test_get_tutorials(mock_list_tutorials, mock_tutorial):
    """Test getting all tutorials."""
    mock_list_tutorials.return_value = [mock_tutorial]

    response = client.get("/api/tutorials/tutorials")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == mock_tutorial.id
    assert response.json()[0]["title"] == mock_tutorial.title
    assert response.json()[0]["level"] == mock_tutorial.level.value
    assert response.json()[0]["section_count"] == len(mock_tutorial.sections)


@patch("tutorials.show_tutorial")
def test_get_tutorial(mock_show_tutorial, mock_tutorial):
    """Test getting a tutorial by ID."""
    mock_show_tutorial.return_value = mock_tutorial

    response = client.get(f"/api/tutorials/tutorials/{mock_tutorial.id}")
    assert response.status_code == 200
    assert response.json()["id"] == mock_tutorial.id
    assert response.json()["title"] == mock_tutorial.title
    assert len(response.json()["sections"]) == len(mock_tutorial.sections)


@patch("tutorials.show_tutorial")
def test_get_tutorial_not_found(mock_show_tutorial):
    """Test getting a non-existent tutorial."""
    mock_show_tutorial.return_value = None

    response = client.get("/api/tutorials/tutorials/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Tutorial not found"


@patch("tutorials.show_tutorial")
def test_get_tutorial_section(mock_show_tutorial, mock_tutorial):
    """Test getting a tutorial section."""
    mock_show_tutorial.return_value = mock_tutorial

    response = client.get(f"/api/tutorials/tutorials/{mock_tutorial.id}/sections/{mock_tutorial.sections[0].id}")
    assert response.status_code == 200
    assert response.json()["id"] == mock_tutorial.sections[0].id
    assert response.json()["title"] == mock_tutorial.sections[0].title
    assert len(response.json()["code_examples"]) == len(mock_tutorial.sections[0].code_examples)
    assert len(response.json()["exercises"]) == len(mock_tutorial.sections[0].exercises)


@patch("tutorials.show_tutorial")
def test_get_tutorial_section_not_found(mock_show_tutorial, mock_tutorial):
    """Test getting a non-existent tutorial section."""
    mock_show_tutorial.return_value = mock_tutorial

    response = client.get(f"/api/tutorials/tutorials/{mock_tutorial.id}/sections/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Section not found"


@patch("tutorials.track_section_completion")
@patch("tutorials.show_tutorial")
def test_update_section_completion(mock_show_tutorial, mock_track_section_completion, mock_tutorial):
    """Test updating section completion status."""
    mock_show_tutorial.return_value = mock_tutorial
    mock_track_section_completion.return_value = {"completed_sections": 1}

    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )

    response = client.post(
        f"/api/tutorials/tutorials/{mock_tutorial.id}/sections/{mock_tutorial.sections[0].id}/completion",
        json={"completed": True},
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert "completed_sections" in response.json()


@patch("tutorials.track_exercise_attempt")
@patch("tutorials.show_tutorial")
def test_submit_exercise(mock_show_tutorial, mock_track_exercise_attempt, mock_tutorial):
    """Test submitting an exercise solution."""
    mock_show_tutorial.return_value = mock_tutorial
    mock_track_exercise_attempt.return_value = {"completed_exercises": 1}

    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )

    response = client.post(
        f"/api/tutorials/tutorials/{mock_tutorial.id}/sections/{mock_tutorial.sections[0].id}/exercises/{mock_tutorial.sections[0].exercises[0].id}",
        json={"code": "print('Solution')"},
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["score"] == 100
    assert "feedback" in response.json()
    assert "progress" in response.json()


@patch("tutorials.get_user_progress")
def test_get_progress(mock_get_user_progress):
    """Test getting user progress."""
    mock_get_user_progress.return_value = {"completed_tutorials": 1}

    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )

    response = client.get(
        "/api/tutorials/progress",
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert "completed_tutorials" in response.json()


@patch("tutorials.set_current_tutorial")
def test_update_current_tutorial(mock_set_current_tutorial):
    """Test updating the current tutorial."""
    mock_set_current_tutorial.return_value = {"current_tutorial": "test-tutorial"}

    # Register a user to get a session
    register_response = client.post(
        "/api/tutorials/users/register",
        json={"username": "testuser"},
    )

    response = client.post(
        "/api/tutorials/progress/current-tutorial",
        json={"tutorial_id": "test-tutorial", "section_id": "section-1"},
        cookies={"session_id": register_response.cookies["session_id"]},
    )
    assert response.status_code == 200
    assert "current_tutorial" in response.json()


def test_get_css():
    """Test getting CSS for tutorials."""
    response = client.get("/api/tutorials/css")
    assert response.status_code == 200
    assert ".tutorial-section" in response.text
    assert ".code-example" in response.text
    assert ".exercise" in response.text
