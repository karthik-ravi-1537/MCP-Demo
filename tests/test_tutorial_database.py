"""Tests for the tutorial database."""

import json
import os
import tempfile
from datetime import datetime
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

from tutorials.database import TutorialDatabase
from tutorials.models import (
    CodeExample,
    DifficultyLevel,
    Exercise,
    Tutorial,
    TutorialSection,
)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[TutorialDatabase, None]:
    """Create a temporary database for testing."""
    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Create the database
    db = TutorialDatabase(db_path)
    await db.connect()
    
    yield db
    
    # Clean up
    await db.close()
    os.unlink(db_path)


@pytest_asyncio.fixture
async def sample_tutorial() -> Tutorial:
    """Create a sample tutorial for testing."""
    return Tutorial(
        id="test-tutorial",
        title="Test Tutorial",
        description="A tutorial for testing",
        level=DifficultyLevel.BEGINNER,
        prerequisites=["none"],
        estimated_time=30,
        created_at=datetime.now(),
        updated_at=datetime.now(),
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
                        expected_output="Hello, world!",
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
                        test_cases=[{"input": {}, "expected": "Solution"}],
                        hints=["Try using print()"],
                        max_attempts=3,
                    ),
                ],
            ),
            TutorialSection(
                id="section-2",
                title="Section 2",
                content="This is section 2",
                code_examples=[],
                exercises=[],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_create_tutorial(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test creating a tutorial."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Get the tutorial
    tutorial = await db.get_tutorial(sample_tutorial.id)
    
    # Check that the tutorial was created
    assert tutorial is not None
    assert tutorial.id == sample_tutorial.id
    assert tutorial.title == sample_tutorial.title
    assert tutorial.description == sample_tutorial.description
    assert tutorial.level == sample_tutorial.level
    assert tutorial.prerequisites == sample_tutorial.prerequisites
    assert tutorial.estimated_time == sample_tutorial.estimated_time
    
    # Check that the sections were created
    assert len(tutorial.sections) == 2
    assert tutorial.sections[0].id == sample_tutorial.sections[0].id
    assert tutorial.sections[0].title == sample_tutorial.sections[0].title
    assert tutorial.sections[0].content == sample_tutorial.sections[0].content
    
    # Check that the code examples were created
    assert len(tutorial.sections[0].code_examples) == 1
    assert tutorial.sections[0].code_examples[0].id == sample_tutorial.sections[0].code_examples[0].id
    assert tutorial.sections[0].code_examples[0].title == sample_tutorial.sections[0].code_examples[0].title
    assert tutorial.sections[0].code_examples[0].code == sample_tutorial.sections[0].code_examples[0].code
    
    # Check that the exercises were created
    assert len(tutorial.sections[0].exercises) == 1
    assert tutorial.sections[0].exercises[0].id == sample_tutorial.sections[0].exercises[0].id
    assert tutorial.sections[0].exercises[0].title == sample_tutorial.sections[0].exercises[0].title
    assert tutorial.sections[0].exercises[0].starter_code == sample_tutorial.sections[0].exercises[0].starter_code


@pytest.mark.asyncio
async def test_update_tutorial(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test updating a tutorial."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Update the tutorial
    sample_tutorial.title = "Updated Title"
    sample_tutorial.sections[0].title = "Updated Section"
    sample_tutorial.sections[0].code_examples[0].title = "Updated Example"
    sample_tutorial.sections[0].exercises[0].title = "Updated Exercise"
    
    await db.update_tutorial(sample_tutorial)
    
    # Get the tutorial
    tutorial = await db.get_tutorial(sample_tutorial.id)
    
    # Check that the tutorial was updated
    assert tutorial is not None
    assert tutorial.title == "Updated Title"
    assert tutorial.sections[0].title == "Updated Section"
    assert tutorial.sections[0].code_examples[0].title == "Updated Example"
    assert tutorial.sections[0].exercises[0].title == "Updated Exercise"


@pytest.mark.asyncio
async def test_delete_tutorial(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test deleting a tutorial."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Delete the tutorial
    result = await db.delete_tutorial(sample_tutorial.id)
    assert result is True
    
    # Check that the tutorial was deleted
    tutorial = await db.get_tutorial(sample_tutorial.id)
    assert tutorial is None
    
    # Try deleting a non-existent tutorial
    result = await db.delete_tutorial("non-existent")
    assert result is False


@pytest.mark.asyncio
async def test_list_tutorials(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test listing tutorials."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Create another tutorial
    another_tutorial = Tutorial(
        id="another-tutorial",
        title="Another Tutorial",
        description="Another tutorial for testing",
        level=DifficultyLevel.INTERMEDIATE,
        prerequisites=["test-tutorial"],
        estimated_time=60,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        sections=[],
    )
    await db.create_tutorial(another_tutorial)
    
    # List all tutorials
    tutorials = await db.list_tutorials()
    assert len(tutorials) == 2
    
    # List beginner tutorials
    beginner_tutorials = await db.list_tutorials(DifficultyLevel.BEGINNER)
    assert len(beginner_tutorials) == 1
    assert beginner_tutorials[0].id == sample_tutorial.id
    
    # List intermediate tutorials
    intermediate_tutorials = await db.list_tutorials(DifficultyLevel.INTERMEDIATE)
    assert len(intermediate_tutorials) == 1
    assert intermediate_tutorials[0].id == another_tutorial.id


@pytest.mark.asyncio
async def test_track_section_completion(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test tracking section completion."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Track section completion
    await db.track_section_completion(
        "test-user",
        sample_tutorial.id,
        sample_tutorial.sections[0].id,
        True,
    )
    
    # Get user progress
    progress = await db.get_user_progress("test-user")
    
    # Check that the section was marked as completed
    assert len(progress["completed_sections"]) == 1
    assert progress["completed_sections"][0]["tutorial_id"] == sample_tutorial.id
    assert progress["completed_sections"][0]["section_id"] == sample_tutorial.sections[0].id
    
    # Track section as not completed
    await db.track_section_completion(
        "test-user",
        sample_tutorial.id,
        sample_tutorial.sections[0].id,
        False,
    )
    
    # Get user progress
    progress = await db.get_user_progress("test-user")
    
    # Check that the section was marked as not completed
    assert len(progress["completed_sections"]) == 0


@pytest.mark.asyncio
async def test_track_exercise_attempt(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test tracking exercise attempts."""
    # Create the tutorial
    await db.create_tutorial(sample_tutorial)
    
    # Track a successful exercise attempt
    await db.track_exercise_attempt(
        "test-user",
        sample_tutorial.sections[0].exercises[0].id,
        "print('Solution')",
        True,
        "Good job!",
    )
    
    # Track a failed exercise attempt
    await db.track_exercise_attempt(
        "test-user",
        sample_tutorial.sections[0].exercises[0].id,
        "print('Wrong')",
        False,
        "Try again",
    )
    
    # Get user progress
    progress = await db.get_user_progress("test-user")
    
    # Check that the attempts were recorded
    assert len(progress["exercise_attempts"]) == 2
    assert progress["exercise_attempts"][0]["exercise_id"] == sample_tutorial.sections[0].exercises[0].id
    assert progress["exercise_attempts"][0]["success"] is False
    assert progress["exercise_attempts"][1]["exercise_id"] == sample_tutorial.sections[0].exercises[0].id
    assert progress["exercise_attempts"][1]["success"] is True
    
    # Check the completion statistics
    assert progress["completed_exercise_count"] == 1
    assert progress["exercise_completion_percentage"] == 100.0


@pytest.mark.asyncio
async def test_import_tutorial_from_file(db: TutorialDatabase, sample_tutorial: Tutorial) -> None:
    """Test importing a tutorial from a file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(json.loads(sample_tutorial.model_dump_json()), f)
        file_path = f.name
    
    try:
        # Import the tutorial
        tutorial = await db.import_tutorial_from_file(file_path)
        
        # Check that the tutorial was imported
        assert tutorial is not None
        assert tutorial.id == sample_tutorial.id
        assert tutorial.title == sample_tutorial.title
        
        # Check that the tutorial is in the database
        db_tutorial = await db.get_tutorial(sample_tutorial.id)
        assert db_tutorial is not None
        assert db_tutorial.id == sample_tutorial.id
    
    finally:
        # Clean up
        os.unlink(file_path)