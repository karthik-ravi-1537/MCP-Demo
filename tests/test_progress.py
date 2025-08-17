"""Tests for the progress tracking system."""

import tempfile
from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from tutorials.database import TutorialDatabase
from tutorials.models import (
    DifficultyLevel,
    Tutorial,
    TutorialSection,
)
from tutorials.progress import Achievement, Certificate, ProgressTracker, UserProgress


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_db() -> MagicMock:
    """Create a mock database."""
    db = MagicMock(spec=TutorialDatabase)

    # Mock the get_tutorial method
    db.get_tutorial.return_value = Tutorial(
        id="test-tutorial",
        title="Test Tutorial",
        description="A tutorial for testing",
        level=DifficultyLevel.BEGINNER,
        prerequisites=[],
        estimated_time=30,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        sections=[
            TutorialSection(
                id="section-1",
                title="Section 1",
                content="This is section 1",
                code_examples=[],
                exercises=[],
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

    # Mock the list_tutorials method
    db.list_tutorials.return_value = [
        # Beginner tutorials
        Tutorial(
            id="beginner-1",
            title="Beginner Tutorial 1",
            description="A beginner tutorial",
            level=DifficultyLevel.BEGINNER,
            prerequisites=[],
            estimated_time=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sections=[
                TutorialSection(
                    id="beginner-1-section-1",
                    title="Section 1",
                    content="This is section 1",
                    code_examples=[],
                    exercises=[],
                ),
            ],
        ),
        Tutorial(
            id="beginner-2",
            title="Beginner Tutorial 2",
            description="Another beginner tutorial",
            level=DifficultyLevel.BEGINNER,
            prerequisites=[],
            estimated_time=30,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sections=[
                TutorialSection(
                    id="beginner-2-section-1",
                    title="Section 1",
                    content="This is section 1",
                    code_examples=[],
                    exercises=[],
                ),
            ],
        ),
        # Intermediate tutorials
        Tutorial(
            id="intermediate-1",
            title="Intermediate Tutorial 1",
            description="An intermediate tutorial",
            level=DifficultyLevel.INTERMEDIATE,
            prerequisites=["beginner-1", "beginner-2"],
            estimated_time=60,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sections=[
                TutorialSection(
                    id="intermediate-1-section-1",
                    title="Section 1",
                    content="This is section 1",
                    code_examples=[],
                    exercises=[],
                ),
            ],
        ),
        # Advanced tutorials
        Tutorial(
            id="advanced-1",
            title="Advanced Tutorial 1",
            description="An advanced tutorial",
            level=DifficultyLevel.ADVANCED,
            prerequisites=["intermediate-1"],
            estimated_time=90,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            sections=[
                TutorialSection(
                    id="advanced-1-section-1",
                    title="Section 1",
                    content="This is section 1",
                    code_examples=[],
                    exercises=[],
                ),
            ],
        ),
    ]

    return db


@pytest.fixture
def tracker(temp_dir: str, mock_db: MagicMock) -> ProgressTracker:
    """Create a progress tracker."""
    return ProgressTracker(mock_db, temp_dir)


def test_load_save_progress(tracker: ProgressTracker) -> None:
    """Test loading and saving progress."""
    # Create a progress object
    progress = UserProgress(
        user_id="test-user",
        completed_tutorials=["tutorial-1", "tutorial-2"],
        completed_sections={"tutorial-1": ["section-1", "section-2"]},
        current_tutorial="tutorial-3",
        current_section="section-1",
        exercise_scores={"exercise-1": 80, "exercise-2": 100},
        achievements=[
            Achievement(
                id="achievement-1",
                name="Achievement 1",
                description="This is achievement 1",
                icon="🏆",
                awarded_at=datetime.now(),
            ),
        ],
        certificates=[
            Certificate(
                id="certificate-1",
                name="Certificate 1",
                description="This is certificate 1",
                level=DifficultyLevel.BEGINNER,
                awarded_at=datetime.now(),
            ),
        ],
        last_active=datetime.now(),
    )

    # Save the progress
    tracker.save_progress(progress)

    # Load the progress
    loaded_progress = tracker.load_progress("test-user")

    # Check that the progress was loaded correctly
    assert loaded_progress.user_id == progress.user_id
    assert loaded_progress.completed_tutorials == progress.completed_tutorials
    assert loaded_progress.completed_sections == progress.completed_sections
    assert loaded_progress.current_tutorial == progress.current_tutorial
    assert loaded_progress.current_section == progress.current_section
    assert loaded_progress.exercise_scores == progress.exercise_scores
    assert len(loaded_progress.achievements) == len(progress.achievements)
    assert loaded_progress.achievements[0].id == progress.achievements[0].id
    assert len(loaded_progress.certificates) == len(progress.certificates)
    assert loaded_progress.certificates[0].id == progress.certificates[0].id


def test_track_section_completion(tracker: ProgressTracker) -> None:
    """Test tracking section completion."""
    # Track section completion
    progress = tracker.track_section_completion(
        "test-user",
        "test-tutorial",
        "section-1",
        True,
    )

    # Check that the section was marked as completed
    assert "test-tutorial" in progress.completed_sections
    assert "section-1" in progress.completed_sections["test-tutorial"]

    # Track section completion for another section
    progress = tracker.track_section_completion(
        "test-user",
        "test-tutorial",
        "section-2",
        True,
    )

    # Check that both sections are marked as completed
    assert "section-1" in progress.completed_sections["test-tutorial"]
    assert "section-2" in progress.completed_sections["test-tutorial"]

    # Check that the tutorial is marked as completed
    assert "test-tutorial" in progress.completed_tutorials

    # Track section as not completed
    progress = tracker.track_section_completion(
        "test-user",
        "test-tutorial",
        "section-1",
        False,
    )

    # Check that the section was marked as not completed
    assert "section-1" not in progress.completed_sections["test-tutorial"]
    assert "section-2" in progress.completed_sections["test-tutorial"]

    # Check that the tutorial is no longer marked as completed
    assert "test-tutorial" not in progress.completed_tutorials


def test_track_exercise_completion(tracker: ProgressTracker) -> None:
    """Test tracking exercise completion."""
    # Track exercise completion
    progress = tracker.track_exercise_completion(
        "test-user",
        "exercise-1",
        80,
    )

    # Check that the exercise score was recorded
    assert "exercise-1" in progress.exercise_scores
    assert progress.exercise_scores["exercise-1"] == 80

    # Track a higher score
    progress = tracker.track_exercise_completion(
        "test-user",
        "exercise-1",
        90,
    )

    # Check that the score was updated
    assert progress.exercise_scores["exercise-1"] == 90

    # Track a lower score
    progress = tracker.track_exercise_completion(
        "test-user",
        "exercise-1",
        70,
    )

    # Check that the score was not updated
    assert progress.exercise_scores["exercise-1"] == 90


def test_set_current_tutorial(tracker: ProgressTracker) -> None:
    """Test setting the current tutorial."""
    # Set the current tutorial
    progress = tracker.set_current_tutorial(
        "test-user",
        "tutorial-1",
        "section-1",
    )

    # Check that the current tutorial and section were set
    assert progress.current_tutorial == "tutorial-1"
    assert progress.current_section == "section-1"

    # Clear the current tutorial and section
    progress = tracker.set_current_tutorial(
        "test-user",
        None,
    )

    # Check that the current tutorial and section were cleared
    assert progress.current_tutorial is None
    assert progress.current_section is None


def test_achievements(tracker: ProgressTracker) -> None:
    """Test achievement tracking."""
    # Create a progress object with completed tutorials
    progress = UserProgress(
        user_id="test-user",
        completed_tutorials=["tutorial-1"],
    )

    # Check for achievements
    tracker._check_achievements(progress)

    # Check that the "First Tutorial" achievement was awarded
    assert any(a.id == "first_tutorial" for a in progress.achievements)

    # Add more completed tutorials
    progress.completed_tutorials.extend(["tutorial-2", "tutorial-3", "tutorial-4", "tutorial-5"])

    # Check for achievements
    tracker._check_achievements(progress)

    # Check that the "Tutorial Master" achievement was awarded
    assert any(a.id == "tutorial_master" for a in progress.achievements)

    # Add exercise scores
    progress.exercise_scores = {f"exercise-{i}": 80 for i in range(10)}

    # Check for achievements
    tracker._check_achievements(progress)

    # Check that the "Exercise Expert" achievement was awarded
    assert any(a.id == "exercise_expert" for a in progress.achievements)

    # Add a perfect score
    progress.exercise_scores["exercise-10"] = 100

    # Check for achievements
    tracker._check_achievements(progress)

    # Check that the "Perfect Score" achievement was awarded
    assert any(a.id == "perfect_score" for a in progress.achievements)


def test_certificates(tracker: ProgressTracker) -> None:
    """Test certificate tracking."""
    # Create a progress object with completed tutorials
    progress = UserProgress(
        user_id="test-user",
        completed_tutorials=["beginner-1", "beginner-2"],
    )

    # Check for certificates
    tracker._check_certificates(progress)

    # Check that the "Beginner Certificate" was awarded
    assert any(c.id == "beginner_certificate" for c in progress.certificates)

    # Add intermediate tutorials
    progress.completed_tutorials.append("intermediate-1")

    # Check for certificates
    tracker._check_certificates(progress)

    # Check that the "Intermediate Certificate" was awarded
    assert any(c.id == "intermediate_certificate" for c in progress.certificates)

    # Add advanced tutorials
    progress.completed_tutorials.append("advanced-1")

    # Check for certificates
    tracker._check_certificates(progress)

    # Check that the "Advanced Certificate" and "MCP Master" were awarded
    assert any(c.id == "advanced_certificate" for c in progress.certificates)
    assert any(c.id == "mcp_master_certificate" for c in progress.certificates)


def test_get_progress_summary(tracker: ProgressTracker) -> None:
    """Test getting a progress summary."""
    # Create a progress object with completed tutorials and sections
    progress = UserProgress(
        user_id="test-user",
        completed_tutorials=["beginner-1"],
        completed_sections={
            "beginner-1": ["beginner-1-section-1"],
            "beginner-2": ["beginner-2-section-1"],
        },
        current_tutorial="intermediate-1",
        current_section="intermediate-1-section-1",
        exercise_scores={"exercise-1": 80, "exercise-2": 100},
        achievements=[
            Achievement(
                id="first_tutorial",
                name="First Tutorial",
                description="Completed your first tutorial",
                icon="🎓",
                awarded_at=datetime.now(),
            ),
        ],
        certificates=[
            Certificate(
                id="beginner_certificate",
                name="Beginner Certificate",
                description="Completed all beginner tutorials",
                level=DifficultyLevel.BEGINNER,
                awarded_at=datetime.now(),
            ),
        ],
    )

    # Save the progress
    tracker.save_progress(progress)

    # Get the progress summary
    summary = tracker.get_progress_summary("test-user")

    # Check the summary
    assert summary["user_id"] == "test-user"
    assert summary["total_tutorials"] == 4
    assert summary["completed_tutorials"] == 1
    assert summary["tutorial_completion_percentage"] == 25.0
    assert summary["total_sections"] == 4
    assert summary["completed_sections"] == 2
    assert summary["section_completion_percentage"] == 50.0
    assert "beginner" in summary["completion_by_level"]
    assert summary["completion_by_level"]["beginner"]["total"] == 2
    assert summary["completion_by_level"]["beginner"]["completed"] == 1
    assert summary["completion_by_level"]["beginner"]["percentage"] == 50.0
    assert len(summary["achievements"]) == 1
    assert summary["achievements"][0]["id"] == "first_tutorial"
    assert len(summary["certificates"]) == 1
    assert summary["certificates"][0]["id"] == "beginner_certificate"
    assert summary["current_tutorial"] == "intermediate-1"
    assert summary["current_section"] == "intermediate-1-section-1"
