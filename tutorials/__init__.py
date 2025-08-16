"""Tutorial management for MCP Demo Project."""

import asyncio
import os
from typing import Dict, List, Optional

from .database import TutorialDatabase
from .models import DifficultyLevel, Tutorial
from .progress import ProgressTracker


# Create global instances
_db = TutorialDatabase(os.environ.get("MCP_DB", "tutorials.db"))
_tracker = ProgressTracker(_db, os.environ.get("MCP_STORAGE", "."))


async def _ensure_db_connected() -> None:
    """Ensure the database is connected."""
    await _db.connect()


async def list_tutorials(level: Optional[str] = None) -> List[Tutorial]:
    """List all available tutorials.
    
    Args:
        level: Optional difficulty level to filter by.
        
    Returns:
        List of tutorials.
    """
    difficulty = DifficultyLevel(level) if level else None
    return await _db.list_tutorials(difficulty)


async def show_tutorial(tutorial_id: str) -> Optional[Tutorial]:
    """Get a tutorial by ID.
    
    Args:
        tutorial_id: ID of the tutorial to get.
        
    Returns:
        The tutorial, or None if not found.
    """
    return await _db.get_tutorial(tutorial_id)


def import_tutorial(path: str) -> Optional[Tutorial]:
    """Import a tutorial from a file.
    
    Args:
        path: Path to the tutorial file.
        
    Returns:
        The imported tutorial, or None if import failed.
    """
    return asyncio.run(_db.import_tutorial_from_file(path))


def import_tutorials_from_directory(directory: str) -> List[Tutorial]:
    """Import tutorials from a directory.
    
    Args:
        directory: Path to the directory containing JSON files.
        
    Returns:
        List of imported tutorials.
    """
    return asyncio.run(_db.import_tutorials_from_directory(directory))


async def track_section_completion(
    user_id: str, tutorial_id: str, section_id: str, completed: bool
) -> Dict:
    """Track completion of a tutorial section.
    
    Args:
        user_id: ID of the user.
        tutorial_id: ID of the tutorial.
        section_id: ID of the section.
        completed: Whether the section is completed.
        
    Returns:
        Dictionary with updated progress information.
    """
    # Track in the database
    await _db.track_section_completion(user_id, tutorial_id, section_id, completed)
    
    # Track in the progress system
    progress = _tracker.track_section_completion(user_id, tutorial_id, section_id, completed)
    
    # Return a summary
    return await _tracker.get_progress_summary(user_id)


async def track_exercise_attempt(
    user_id: str,
    exercise_id: str,
    code: str,
    success: bool,
    score: int = 0,
    feedback: Optional[str] = None,
) -> Dict:
    """Track an exercise attempt.
    
    Args:
        user_id: ID of the user.
        exercise_id: ID of the exercise.
        code: Code submitted by the user.
        success: Whether the attempt was successful.
        score: Score achieved (0-100).
        feedback: Feedback for the attempt.
        
    Returns:
        Dictionary with updated progress information.
    """
    # Track in the database
    await _db.track_exercise_attempt(user_id, exercise_id, code, success, feedback)
    
    # Track in the progress system
    progress = _tracker.track_exercise_completion(user_id, exercise_id, score)
    
    # Return a summary
    return await _tracker.get_progress_summary(user_id)


async def get_user_progress(user_id: str) -> Dict:
    """Get a user's progress.
    
    Args:
        user_id: ID of the user.
        
    Returns:
        Dictionary with progress information.
    """
    return await _tracker.get_progress_summary(user_id)


async def set_current_tutorial(
    user_id: str, tutorial_id: Optional[str], section_id: Optional[str] = None
) -> Dict:
    """Set the current tutorial and section.
    
    Args:
        user_id: ID of the user.
        tutorial_id: ID of the tutorial, or None to clear.
        section_id: ID of the section, or None to clear.
        
    Returns:
        Dictionary with updated progress information.
    """
    # Track in the progress system
    progress = _tracker.set_current_tutorial(user_id, tutorial_id, section_id)
    
    # Return a summary
    return await _tracker.get_progress_summary(user_id)