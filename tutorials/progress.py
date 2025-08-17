"""Progress tracking system for tutorials."""

import json
import logging
import os
from datetime import datetime

from pydantic import BaseModel, Field

from .database import TutorialDatabase
from .models import DifficultyLevel

# Set up logging
logger = logging.getLogger(__name__)


class Achievement(BaseModel):
    """Achievement model."""

    id: str
    name: str
    description: str
    icon: str
    awarded_at: datetime = Field(default_factory=datetime.now)


class Certificate(BaseModel):
    """Certificate model."""

    id: str
    name: str
    description: str
    awarded_at: datetime = Field(default_factory=datetime.now)
    level: DifficultyLevel


class UserProgress(BaseModel):
    """User progress model."""

    user_id: str
    completed_tutorials: list[str] = Field(default_factory=list)
    completed_sections: dict[str, list[str]] = Field(default_factory=dict)
    current_tutorial: str | None = None
    current_section: str | None = None
    exercise_scores: dict[str, int] = Field(default_factory=dict)
    achievements: list[Achievement] = Field(default_factory=list)
    certificates: list[Certificate] = Field(default_factory=list)
    last_active: datetime = Field(default_factory=datetime.now)


class ProgressTracker:
    """Progress tracking system for tutorials."""

    def __init__(self, db: TutorialDatabase, storage_dir: str = "."):
        """Initialize the progress tracker.

        Args:
            db: Tutorial database.
            storage_dir: Directory to store progress files.
        """
        self.db = db
        self.storage_dir = storage_dir
        self.progress_dir = os.path.join(storage_dir, "progress")

        # Create the progress directory if it doesn't exist
        os.makedirs(self.progress_dir, exist_ok=True)

    def _get_progress_path(self, user_id: str) -> str:
        """Get the path to a user's progress file.

        Args:
            user_id: ID of the user.

        Returns:
            Path to the progress file.
        """
        return os.path.join(self.progress_dir, f"{user_id}.json")

    def load_progress(self, user_id: str) -> UserProgress:
        """Load a user's progress.

        Args:
            user_id: ID of the user.

        Returns:
            The user's progress.
        """
        path = self._get_progress_path(user_id)

        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)

                return UserProgress.model_validate(data)

            except Exception as e:
                logger.error(f"Error loading progress for user {user_id}: {e}")

        # Return a new progress object if the file doesn't exist or there was an error
        return UserProgress(user_id=user_id)

    def save_progress(self, progress: UserProgress) -> None:
        """Save a user's progress.

        Args:
            progress: The user's progress.
        """
        path = self._get_progress_path(progress.user_id)

        try:
            # Update the last active timestamp
            progress.last_active = datetime.now()

            # Save the progress
            with open(path, "w") as f:
                json.dump(json.loads(progress.model_dump_json()), f, indent=2)

        except Exception as e:
            logger.error(f"Error saving progress for user {progress.user_id}: {e}")

    def track_section_completion(
        self, user_id: str, tutorial_id: str, section_id: str, completed: bool
    ) -> UserProgress:
        """Track completion of a tutorial section.

        Args:
            user_id: ID of the user.
            tutorial_id: ID of the tutorial.
            section_id: ID of the section.
            completed: Whether the section is completed.

        Returns:
            The updated user progress.
        """
        # Load the user's progress
        progress = self.load_progress(user_id)

        # Initialize the tutorial's sections if needed
        if tutorial_id not in progress.completed_sections:
            progress.completed_sections[tutorial_id] = []

        # Update the section completion
        if completed and section_id not in progress.completed_sections[tutorial_id]:
            progress.completed_sections[tutorial_id].append(section_id)
        elif not completed and section_id in progress.completed_sections[tutorial_id]:
            progress.completed_sections[tutorial_id].remove(section_id)

        # Check if the tutorial is completed
        self._check_tutorial_completion(progress, tutorial_id)

        # Check for achievements
        self._check_achievements(progress)

        # Check for certificates
        self._check_certificates(progress)

        # Save the progress
        self.save_progress(progress)

        return progress

    def track_exercise_completion(self, user_id: str, exercise_id: str, score: int) -> UserProgress:
        """Track completion of an exercise.

        Args:
            user_id: ID of the user.
            exercise_id: ID of the exercise.
            score: Score achieved.

        Returns:
            The updated user progress.
        """
        # Load the user's progress
        progress = self.load_progress(user_id)

        # Update the exercise score
        progress.exercise_scores[exercise_id] = max(
            progress.exercise_scores.get(exercise_id, 0),
            score,
        )

        # Check for achievements
        self._check_achievements(progress)

        # Save the progress
        self.save_progress(progress)

        return progress

    def set_current_tutorial(
        self, user_id: str, tutorial_id: str | None, section_id: str | None = None
    ) -> UserProgress:
        """Set the current tutorial and section.

        Args:
            user_id: ID of the user.
            tutorial_id: ID of the tutorial, or None to clear.
            section_id: ID of the section, or None to clear.

        Returns:
            The updated user progress.
        """
        # Load the user's progress
        progress = self.load_progress(user_id)

        # Update the current tutorial and section
        progress.current_tutorial = tutorial_id
        progress.current_section = section_id

        # Save the progress
        self.save_progress(progress)

        return progress

    def _check_tutorial_completion(self, progress: UserProgress, tutorial_id: str) -> None:
        """Check if a tutorial is completed.

        Args:
            progress: The user's progress.
            tutorial_id: ID of the tutorial to check.
        """
        # Get the tutorial
        tutorial = self.db.get_tutorial(tutorial_id)
        if tutorial is None:
            return

        # Get the sections in the tutorial
        section_ids = {section.id for section in tutorial.sections}

        # Get the completed sections
        completed_section_ids = set(progress.completed_sections.get(tutorial_id, []))

        # Check if all sections are completed
        if section_ids.issubset(completed_section_ids) and tutorial_id not in progress.completed_tutorials:
            progress.completed_tutorials.append(tutorial_id)

    def _check_achievements(self, progress: UserProgress) -> None:
        """Check for achievements.

        Args:
            progress: The user's progress.
        """
        # Get the IDs of existing achievements
        existing_achievement_ids = {achievement.id for achievement in progress.achievements}

        # Check for the "First Tutorial" achievement
        if len(progress.completed_tutorials) >= 1 and "first_tutorial" not in existing_achievement_ids:
            progress.achievements.append(
                Achievement(
                    id="first_tutorial",
                    name="First Tutorial",
                    description="Completed your first tutorial",
                    icon="🎓",
                )
            )

        # Check for the "Tutorial Master" achievement
        if len(progress.completed_tutorials) >= 5 and "tutorial_master" not in existing_achievement_ids:
            progress.achievements.append(
                Achievement(
                    id="tutorial_master",
                    name="Tutorial Master",
                    description="Completed 5 tutorials",
                    icon="🏆",
                )
            )

        # Check for the "Exercise Expert" achievement
        if len(progress.exercise_scores) >= 10 and "exercise_expert" not in existing_achievement_ids:
            progress.achievements.append(
                Achievement(
                    id="exercise_expert",
                    name="Exercise Expert",
                    description="Completed 10 exercises",
                    icon="💪",
                )
            )

        # Check for the "Perfect Score" achievement
        if (
            any(score == 100 for score in progress.exercise_scores.values())
            and "perfect_score" not in existing_achievement_ids
        ):
            progress.achievements.append(
                Achievement(
                    id="perfect_score",
                    name="Perfect Score",
                    description="Achieved a perfect score on an exercise",
                    icon="🌟",
                )
            )

    def _check_certificates(self, progress: UserProgress) -> None:
        """Check for certificates.

        Args:
            progress: The user's progress.
        """
        # Get the IDs of existing certificates
        existing_certificate_ids = {certificate.id for certificate in progress.certificates}

        # Get all tutorials
        tutorials = self.db.list_tutorials()

        # Group tutorials by level
        beginner_tutorials = [t.id for t in tutorials if t.level == DifficultyLevel.BEGINNER]
        intermediate_tutorials = [t.id for t in tutorials if t.level == DifficultyLevel.INTERMEDIATE]
        advanced_tutorials = [t.id for t in tutorials if t.level == DifficultyLevel.ADVANCED]

        # Check for the "Beginner Certificate"
        if (
            all(tutorial_id in progress.completed_tutorials for tutorial_id in beginner_tutorials)
            and beginner_tutorials
            and "beginner_certificate" not in existing_certificate_ids
        ):
            progress.certificates.append(
                Certificate(
                    id="beginner_certificate",
                    name="Beginner Certificate",
                    description="Completed all beginner tutorials",
                    level=DifficultyLevel.BEGINNER,
                )
            )

        # Check for the "Intermediate Certificate"
        if (
            all(tutorial_id in progress.completed_tutorials for tutorial_id in intermediate_tutorials)
            and intermediate_tutorials
            and "intermediate_certificate" not in existing_certificate_ids
        ):
            progress.certificates.append(
                Certificate(
                    id="intermediate_certificate",
                    name="Intermediate Certificate",
                    description="Completed all intermediate tutorials",
                    level=DifficultyLevel.INTERMEDIATE,
                )
            )

        # Check for the "Advanced Certificate"
        if (
            all(tutorial_id in progress.completed_tutorials for tutorial_id in advanced_tutorials)
            and advanced_tutorials
            and "advanced_certificate" not in existing_certificate_ids
        ):
            progress.certificates.append(
                Certificate(
                    id="advanced_certificate",
                    name="Advanced Certificate",
                    description="Completed all advanced tutorials",
                    level=DifficultyLevel.ADVANCED,
                )
            )

        # Check for the "MCP Master" certificate
        if (
            all(
                tutorial_id in progress.completed_tutorials
                for tutorial_id in beginner_tutorials + intermediate_tutorials + advanced_tutorials
            )
            and beginner_tutorials
            and intermediate_tutorials
            and advanced_tutorials
            and "mcp_master_certificate" not in existing_certificate_ids
        ):
            progress.certificates.append(
                Certificate(
                    id="mcp_master_certificate",
                    name="MCP Master",
                    description="Completed all tutorials",
                    level=DifficultyLevel.ADVANCED,
                )
            )

    async def get_progress_summary(self, user_id: str) -> dict:
        """Get a summary of a user's progress.

        Args:
            user_id: ID of the user.

        Returns:
            Dictionary with progress summary.
        """
        # Load the user's progress
        progress = self.load_progress(user_id)

        # Get all tutorials
        tutorials = await self.db.list_tutorials()

        # Calculate statistics
        total_tutorials = len(tutorials)
        completed_tutorials = len(progress.completed_tutorials)

        total_sections = sum(len(tutorial.sections) for tutorial in tutorials)
        completed_sections = sum(len(sections) for sections in progress.completed_sections.values())

        # Group tutorials by level
        tutorials_by_level = {
            DifficultyLevel.BEGINNER: [t for t in tutorials if t.level == DifficultyLevel.BEGINNER],
            DifficultyLevel.INTERMEDIATE: [t for t in tutorials if t.level == DifficultyLevel.INTERMEDIATE],
            DifficultyLevel.ADVANCED: [t for t in tutorials if t.level == DifficultyLevel.ADVANCED],
        }

        # Calculate completion by level
        completion_by_level = {}
        for level, level_tutorials in tutorials_by_level.items():
            total = len(level_tutorials)
            completed = len([t for t in level_tutorials if t.id in progress.completed_tutorials])
            completion_by_level[level.value] = {
                "total": total,
                "completed": completed,
                "percentage": (completed / total * 100) if total > 0 else 0,
            }

        return {
            "user_id": user_id,
            "total_tutorials": total_tutorials,
            "completed_tutorials": completed_tutorials,
            "tutorial_completion_percentage": (
                (completed_tutorials / total_tutorials * 100) if total_tutorials > 0 else 0
            ),
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "section_completion_percentage": (completed_sections / total_sections * 100) if total_sections > 0 else 0,
            "completion_by_level": completion_by_level,
            "achievements": [
                {
                    "id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "awarded_at": achievement.awarded_at.isoformat(),
                }
                for achievement in progress.achievements
            ],
            "certificates": [
                {
                    "id": certificate.id,
                    "name": certificate.name,
                    "description": certificate.description,
                    "level": certificate.level.value,
                    "awarded_at": certificate.awarded_at.isoformat(),
                }
                for certificate in progress.certificates
            ],
            "current_tutorial": progress.current_tutorial,
            "current_section": progress.current_section,
            "last_active": progress.last_active.isoformat(),
        }
