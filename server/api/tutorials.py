"""API endpoints for tutorials."""

import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from pydantic import BaseModel

from tutorials import (
    get_user_progress,
    list_tutorials,
    set_current_tutorial,
    show_tutorial,
    track_exercise_attempt,
    track_section_completion,
)
from tutorials.models import DifficultyLevel, Tutorial
from tutorials.renderer import TutorialRenderer

from .sessions import SessionData, create_session, get_active_session, get_session


# Create router
router = APIRouter()

# Create renderer
renderer = TutorialRenderer()


class ExerciseSubmission(BaseModel):
    """Exercise submission model."""
    
    code: str


class SectionCompletionUpdate(BaseModel):
    """Section completion update model."""
    
    completed: bool


class CurrentTutorialUpdate(BaseModel):
    """Current tutorial update model."""
    
    tutorial_id: Optional[str] = None
    section_id: Optional[str] = None


class UserRegistration(BaseModel):
    """User registration model."""
    
    username: str


class UserLogin(BaseModel):
    """User login model."""
    
    username: str


@router.post("/users/register", response_model=Dict)
async def register_user(registration: UserRegistration, response: Response):
    """Register a new user."""
    # In a real application, you would check if the username is available
    # and store the user in a database
    
    # Generate a user ID
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Create a session
    session_id = create_session(response, user_id)
    
    return {
        "user_id": user_id,
        "username": registration.username,
        "session_id": session_id,
    }


@router.post("/users/login", response_model=Dict)
async def login_user(login: UserLogin, response: Response):
    """Log in a user."""
    # In a real application, you would validate the username and password
    # against a database
    
    # For this demo, we'll just create a new user ID
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # Create a session
    session_id = create_session(response, user_id)
    
    return {
        "user_id": user_id,
        "username": login.username,
        "session_id": session_id,
    }


@router.get("/users/me", response_model=Dict)
async def get_current_user(session: SessionData = Depends(get_active_session)):
    """Get the current user."""
    return {
        "user_id": session.user_id,
        "last_active": session.last_active,
    }


@router.get("/tutorials", response_model=List[Dict])
async def get_tutorials(
    level: Optional[str] = Query(None, description="Filter by difficulty level")
):
    """Get all tutorials."""
    tutorials = await list_tutorials(level)
    
    # Convert tutorials to dictionaries
    return [
        {
            "id": tutorial.id,
            "title": tutorial.title,
            "description": tutorial.description,
            "level": tutorial.level.value,
            "prerequisites": tutorial.prerequisites,
            "estimated_time": tutorial.estimated_time,
            "section_count": len(tutorial.sections),
        }
        for tutorial in tutorials
    ]


@router.get("/tutorials/{tutorial_id}", response_model=Dict)
async def get_tutorial(
    tutorial_id: str = Path(..., description="ID of the tutorial to get")
):
    """Get a tutorial by ID."""
    tutorial = await show_tutorial(tutorial_id)
    
    if tutorial is None:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Render the tutorial
    return renderer.render_tutorial(tutorial)


@router.get("/tutorials/{tutorial_id}/sections/{section_id}", response_model=Dict)
async def get_tutorial_section(
    tutorial_id: str = Path(..., description="ID of the tutorial"),
    section_id: str = Path(..., description="ID of the section"),
):
    """Get a tutorial section."""
    tutorial = await show_tutorial(tutorial_id)
    
    if tutorial is None:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Find the section
    section = next((s for s in tutorial.sections if s.id == section_id), None)
    
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Render the section
    return renderer.render_section(section)


@router.post("/tutorials/{tutorial_id}/sections/{section_id}/completion", response_model=Dict)
async def update_section_completion(
    update: SectionCompletionUpdate,
    tutorial_id: str = Path(..., description="ID of the tutorial"),
    section_id: str = Path(..., description="ID of the section"),
    session: SessionData = Depends(get_active_session),
):
    """Update section completion status."""
    tutorial = await show_tutorial(tutorial_id)
    
    if tutorial is None:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Find the section
    section = next((s for s in tutorial.sections if s.id == section_id), None)
    
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Update the completion status
    progress = await track_section_completion(
        session.user_id, tutorial_id, section_id, update.completed
    )
    
    return progress


@router.post("/tutorials/{tutorial_id}/sections/{section_id}/exercises/{exercise_id}", response_model=Dict)
async def submit_exercise(
    submission: ExerciseSubmission,
    tutorial_id: str = Path(..., description="ID of the tutorial"),
    section_id: str = Path(..., description="ID of the section"),
    exercise_id: str = Path(..., description="ID of the exercise"),
    session: SessionData = Depends(get_active_session),
):
    """Submit an exercise solution."""
    tutorial = await show_tutorial(tutorial_id)
    
    if tutorial is None:
        raise HTTPException(status_code=404, detail="Tutorial not found")
    
    # Find the section
    section = next((s for s in tutorial.sections if s.id == section_id), None)
    
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Find the exercise
    exercise = next((e for e in section.exercises if e.id == exercise_id), None)
    
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Validate the submission
    # This is a simplified validation - in a real application, you would run tests
    success = submission.code.strip() == exercise.solution_code.strip()
    score = 100 if success else 0
    feedback = "Correct solution!" if success else "Incorrect solution. Try again."
    
    # Track the attempt
    progress = await track_exercise_attempt(
        session.user_id, exercise_id, submission.code, success, score, feedback
    )
    
    return {
        "success": success,
        "score": score,
        "feedback": feedback,
        "progress": progress,
    }


@router.get("/progress", response_model=Dict)
async def get_progress(
    session: SessionData = Depends(get_active_session)
):
    """Get the current user's progress."""
    return await get_user_progress(session.user_id)


@router.post("/progress/current-tutorial", response_model=Dict)
async def update_current_tutorial(
    update: CurrentTutorialUpdate,
    session: SessionData = Depends(get_active_session),
):
    """Update the current tutorial and section."""
    return await set_current_tutorial(
        session.user_id, update.tutorial_id, update.section_id
    )


@router.get("/css")
async def get_css():
    """Get CSS for tutorials."""
    from fastapi import Response
    css_content = renderer.get_css()
    return Response(content=css_content, media_type="text/css")