"""Database access layer for tutorials."""

import json
import logging
import pathlib
from datetime import datetime
from typing import Any

import aiosqlite

from .models import CodeExample, DifficultyLevel, Exercise, Tutorial, TutorialSection

# Set up logging
logger = logging.getLogger(__name__)


class TutorialDatabase:
    """Database access layer for tutorials."""

    def __init__(self, db_path: str = "tutorials.db"):
        """Initialize the database.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Connect to the database."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
            await self._create_tables()

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        if self._connection is None:
            raise RuntimeError("Database not connected")

        # Create tutorials table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tutorials (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                level TEXT NOT NULL,
                prerequisites TEXT NOT NULL,
                estimated_time INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """
        )

        # Create tutorial sections table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tutorial_sections (
                id TEXT PRIMARY KEY,
                tutorial_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (tutorial_id) REFERENCES tutorials (id) ON DELETE CASCADE
            )
        """
        )

        # Create code examples table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS code_examples (
                id TEXT PRIMARY KEY,
                section_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                expected_output TEXT,
                position INTEGER NOT NULL,
                FOREIGN KEY (section_id) REFERENCES tutorial_sections (id) ON DELETE CASCADE
            )
        """
        )

        # Create exercises table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id TEXT PRIMARY KEY,
                section_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                starter_code TEXT NOT NULL,
                solution_code TEXT NOT NULL,
                test_cases TEXT NOT NULL,
                hints TEXT NOT NULL,
                max_attempts INTEGER NOT NULL,
                position INTEGER NOT NULL,
                FOREIGN KEY (section_id) REFERENCES tutorial_sections (id) ON DELETE CASCADE
            )
        """
        )

        # Create user progress table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT NOT NULL,
                tutorial_id TEXT NOT NULL,
                section_id TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                completed_at TIMESTAMP,
                PRIMARY KEY (user_id, tutorial_id, section_id),
                FOREIGN KEY (tutorial_id) REFERENCES tutorials (id) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES tutorial_sections (id) ON DELETE CASCADE
            )
        """
        )

        # Create exercise attempts table
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS exercise_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                exercise_id TEXT NOT NULL,
                code TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
            )
        """
        )

        await self._connection.commit()

    async def get_tutorial(self, tutorial_id: str) -> Tutorial | None:
        """Get a tutorial by ID.

        Args:
            tutorial_id: ID of the tutorial to get.

        Returns:
            The tutorial, or None if not found.
        """
        if self._connection is None:
            await self.connect()

        # Get the tutorial
        async with self._connection.execute("SELECT * FROM tutorials WHERE id = ?", (tutorial_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None

            tutorial_data = dict(row)
            tutorial_data["prerequisites"] = json.loads(tutorial_data["prerequisites"])
            tutorial_data["level"] = DifficultyLevel(tutorial_data["level"])
            tutorial_data["created_at"] = datetime.fromisoformat(tutorial_data["created_at"])
            tutorial_data["updated_at"] = datetime.fromisoformat(tutorial_data["updated_at"])

            # Get the sections
            sections = await self.get_tutorial_sections(tutorial_id)
            tutorial_data["sections"] = sections

            return Tutorial(**tutorial_data)

    async def get_tutorial_sections(self, tutorial_id: str) -> list[TutorialSection]:
        """Get the sections of a tutorial.

        Args:
            tutorial_id: ID of the tutorial.

        Returns:
            List of tutorial sections.
        """
        if self._connection is None:
            await self.connect()

        sections = []

        # Get the sections
        async with self._connection.execute(
            "SELECT * FROM tutorial_sections WHERE tutorial_id = ? ORDER BY position",
            (tutorial_id,),
        ) as cursor:
            async for row in cursor:
                section_data = dict(row)
                section_id = section_data["id"]

                # Get code examples
                code_examples = await self.get_section_code_examples(section_id)

                # Get exercises
                exercises = await self.get_section_exercises(section_id)

                # Create the section
                section = TutorialSection(
                    id=section_data["id"],
                    title=section_data["title"],
                    content=section_data["content"],
                    code_examples=code_examples,
                    exercises=exercises,
                )

                sections.append(section)

        return sections

    async def get_section_code_examples(self, section_id: str) -> list[CodeExample]:
        """Get the code examples of a tutorial section.

        Args:
            section_id: ID of the section.

        Returns:
            List of code examples.
        """
        if self._connection is None:
            await self.connect()

        code_examples = []

        # Get the code examples
        async with self._connection.execute(
            "SELECT * FROM code_examples WHERE section_id = ? ORDER BY position",
            (section_id,),
        ) as cursor:
            async for row in cursor:
                example_data = dict(row)

                # Create the code example
                example = CodeExample(
                    id=example_data["id"],
                    title=example_data["title"],
                    description=example_data["description"],
                    code=example_data["code"],
                    language=example_data["language"],
                    expected_output=example_data["expected_output"],
                )

                code_examples.append(example)

        return code_examples

    async def get_section_exercises(self, section_id: str) -> list[Exercise]:
        """Get the exercises of a tutorial section.

        Args:
            section_id: ID of the section.

        Returns:
            List of exercises.
        """
        if self._connection is None:
            await self.connect()

        exercises = []

        # Get the exercises
        async with self._connection.execute(
            "SELECT * FROM exercises WHERE section_id = ? ORDER BY position",
            (section_id,),
        ) as cursor:
            async for row in cursor:
                exercise_data = dict(row)

                # Parse JSON fields
                test_cases = json.loads(exercise_data["test_cases"])
                hints = json.loads(exercise_data["hints"])

                # Create the exercise
                exercise = Exercise(
                    id=exercise_data["id"],
                    title=exercise_data["title"],
                    description=exercise_data["description"],
                    difficulty=DifficultyLevel(exercise_data["difficulty"]),
                    starter_code=exercise_data["starter_code"],
                    solution_code=exercise_data["solution_code"],
                    test_cases=test_cases,
                    hints=hints,
                    max_attempts=exercise_data["max_attempts"],
                )

                exercises.append(exercise)

        return exercises

    async def list_tutorials(self, level: DifficultyLevel | None = None) -> list[Tutorial]:
        """List all tutorials.

        Args:
            level: Optional difficulty level to filter by.

        Returns:
            List of tutorials.
        """
        if self._connection is None:
            await self.connect()

        tutorials = []

        # Build the query
        query = "SELECT * FROM tutorials"
        params = []

        if level is not None:
            query += " WHERE level = ?"
            params.append(level.value)

        query += " ORDER BY created_at DESC"

        # Get the tutorials
        async with self._connection.execute(query, params) as cursor:
            async for row in cursor:
                tutorial_data = dict(row)
                tutorial_id = tutorial_data["id"]

                # Get the sections
                sections = await self.get_tutorial_sections(tutorial_id)

                # Parse JSON and datetime fields
                tutorial_data["prerequisites"] = json.loads(tutorial_data["prerequisites"])
                tutorial_data["level"] = DifficultyLevel(tutorial_data["level"])
                tutorial_data["created_at"] = datetime.fromisoformat(tutorial_data["created_at"])
                tutorial_data["updated_at"] = datetime.fromisoformat(tutorial_data["updated_at"])

                # Create the tutorial
                tutorial = Tutorial(
                    **tutorial_data,
                    sections=sections,
                )

                tutorials.append(tutorial)

        return tutorials

    async def create_tutorial(self, tutorial: Tutorial) -> None:
        """Create a new tutorial.

        Args:
            tutorial: The tutorial to create.
        """
        if self._connection is None:
            await self.connect()

        # Start a transaction
        await self._connection.execute("BEGIN")
        try:
            # Insert the tutorial
            await self._connection.execute(
                """
                INSERT INTO tutorials (
                    id, title, description, level, prerequisites,
                    estimated_time, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tutorial.id,
                    tutorial.title,
                    tutorial.description,
                    tutorial.level.value,
                    json.dumps(tutorial.prerequisites),
                    tutorial.estimated_time,
                    tutorial.created_at.isoformat(),
                    tutorial.updated_at.isoformat(),
                ),
            )

            # Insert the sections
            for i, section in enumerate(tutorial.sections):
                await self._connection.execute(
                    """
                    INSERT INTO tutorial_sections (
                        id, tutorial_id, title, content, position
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        section.id,
                        tutorial.id,
                        section.title,
                        section.content,
                        i,
                    ),
                )

                # Insert code examples
                for j, example in enumerate(section.code_examples):
                    await self._connection.execute(
                        """
                        INSERT INTO code_examples (
                            id, section_id, title, description,
                            code, language, expected_output, position
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            example.id,
                            section.id,
                            example.title,
                            example.description,
                            example.code,
                            example.language,
                            example.expected_output,
                            j,
                        ),
                    )

                # Insert exercises
                for j, exercise in enumerate(section.exercises):
                    await self._connection.execute(
                        """
                        INSERT INTO exercises (
                            id, section_id, title, description,
                            difficulty, starter_code, solution_code,
                            test_cases, hints, max_attempts, position
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            exercise.id,
                            section.id,
                            exercise.title,
                            exercise.description,
                            exercise.difficulty.value,
                            exercise.starter_code,
                            exercise.solution_code,
                            json.dumps(exercise.test_cases),
                            json.dumps(exercise.hints),
                            exercise.max_attempts,
                            j,
                        ),
                    )

            # Commit the transaction
            await self._connection.commit()
        except Exception:
            # Rollback on error
            await self._connection.rollback()
            raise

    async def update_tutorial(self, tutorial: Tutorial) -> None:
        """Update an existing tutorial.

        Args:
            tutorial: The tutorial to update.
        """
        if self._connection is None:
            await self.connect()

        # Check if the tutorial exists
        existing = await self.get_tutorial(tutorial.id)
        if existing is None:
            raise ValueError(f"Tutorial {tutorial.id} not found")

        # Start a transaction
        await self._connection.execute("BEGIN")
        try:
            # Update the tutorial
            await self._connection.execute(
                """
                UPDATE tutorials SET
                    title = ?,
                    description = ?,
                    level = ?,
                    prerequisites = ?,
                    estimated_time = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    tutorial.title,
                    tutorial.description,
                    tutorial.level.value,
                    json.dumps(tutorial.prerequisites),
                    tutorial.estimated_time,
                    tutorial.updated_at.isoformat(),
                    tutorial.id,
                ),
            )

            # Delete existing sections, code examples, and exercises
            await self._connection.execute(
                "DELETE FROM exercises WHERE section_id IN (SELECT id FROM tutorial_sections WHERE tutorial_id = ?)",
                (tutorial.id,),
            )
            await self._connection.execute(
                "DELETE FROM code_examples WHERE section_id IN (SELECT id FROM tutorial_sections WHERE tutorial_id = ?)",
                (tutorial.id,),
            )
            await self._connection.execute("DELETE FROM tutorial_sections WHERE tutorial_id = ?", (tutorial.id,))

            # Insert the sections
            for i, section in enumerate(tutorial.sections):
                await self._connection.execute(
                    """
                    INSERT INTO tutorial_sections (
                        id, tutorial_id, title, content, position
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        section.id,
                        tutorial.id,
                        section.title,
                        section.content,
                        i,
                    ),
                )

                # Insert code examples
                for j, example in enumerate(section.code_examples):
                    await self._connection.execute(
                        """
                        INSERT INTO code_examples (
                            id, section_id, title, description,
                            code, language, expected_output, position
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            example.id,
                            section.id,
                            example.title,
                            example.description,
                            example.code,
                            example.language,
                            example.expected_output,
                            j,
                        ),
                    )

                # Insert exercises
                for j, exercise in enumerate(section.exercises):
                    await self._connection.execute(
                        """
                        INSERT INTO exercises (
                            id, section_id, title, description,
                            difficulty, starter_code, solution_code,
                            test_cases, hints, max_attempts, position
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            exercise.id,
                            section.id,
                            exercise.title,
                            exercise.description,
                            exercise.difficulty.value,
                            exercise.starter_code,
                            exercise.solution_code,
                            json.dumps(exercise.test_cases),
                            json.dumps(exercise.hints),
                            exercise.max_attempts,
                            j,
                        ),
                    )

            # Commit the transaction
            await self._connection.commit()
        except Exception:
            # Rollback on error
            await self._connection.rollback()
            raise

    async def delete_tutorial(self, tutorial_id: str) -> bool:
        """Delete a tutorial.

        Args:
            tutorial_id: ID of the tutorial to delete.

        Returns:
            True if the tutorial was deleted, False if it wasn't found.
        """
        if self._connection is None:
            await self.connect()

        # Start a transaction
        await self._connection.execute("BEGIN")
        try:
            # Delete the tutorial
            cursor = await self._connection.execute("DELETE FROM tutorials WHERE id = ?", (tutorial_id,))

            # Commit the transaction
            await self._connection.commit()

            return cursor.rowcount > 0
        except Exception:
            # Rollback on error
            await self._connection.rollback()
            raise

    async def import_tutorial_from_file(self, file_path: str) -> Tutorial | None:
        """Import a tutorial from a JSON file.

        Args:
            file_path: Path to the JSON file.

        Returns:
            The imported tutorial, or None if import failed.
        """
        try:
            # Read the file
            with open(file_path) as f:
                data = json.load(f)

            # Parse the tutorial
            tutorial = Tutorial.model_validate(data)

            # Create the tutorial in the database
            await self.create_tutorial(tutorial)

            return tutorial

        except Exception as e:
            logger.error(f"Error importing tutorial from {file_path}: {e}")
            return None

    async def import_tutorials_from_directory(self, directory: str) -> list[Tutorial]:
        """Import tutorials from a directory.

        Args:
            directory: Path to the directory containing JSON files.

        Returns:
            List of imported tutorials.
        """
        tutorials = []

        # Get all JSON files in the directory
        for file_path in pathlib.Path(directory).glob("*.json"):
            tutorial = await self.import_tutorial_from_file(str(file_path))
            if tutorial is not None:
                tutorials.append(tutorial)

        return tutorials

    async def track_section_completion(self, user_id: str, tutorial_id: str, section_id: str, completed: bool) -> None:
        """Track completion of a tutorial section.

        Args:
            user_id: ID of the user.
            tutorial_id: ID of the tutorial.
            section_id: ID of the section.
            completed: Whether the section is completed.
        """
        if self._connection is None:
            await self.connect()

        # Start a transaction
        await self._connection.execute("BEGIN")
        try:
            # Check if there's an existing record
            cursor = await self._connection.execute(
                """
                SELECT * FROM user_progress
                WHERE user_id = ? AND tutorial_id = ? AND section_id = ?
                """,
                (user_id, tutorial_id, section_id),
            )
            existing = await cursor.fetchone()

            if existing is None:
                # Insert a new record
                await self._connection.execute(
                    """
                    INSERT INTO user_progress (
                        user_id, tutorial_id, section_id, completed, completed_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        tutorial_id,
                        section_id,
                        completed,
                        datetime.now().isoformat() if completed else None,
                    ),
                )
            else:
                # Update the existing record
                await self._connection.execute(
                    """
                    UPDATE user_progress SET
                        completed = ?,
                        completed_at = ?
                    WHERE user_id = ? AND tutorial_id = ? AND section_id = ?
                    """,
                    (
                        completed,
                        datetime.now().isoformat() if completed else None,
                        user_id,
                        tutorial_id,
                        section_id,
                    ),
                )

            # Commit the transaction
            await self._connection.commit()
        except Exception:
            # Rollback on error
            await self._connection.rollback()
            raise

    async def track_exercise_attempt(
        self,
        user_id: str,
        exercise_id: str,
        code: str,
        success: bool,
        feedback: str | None = None,
    ) -> None:
        """Track an exercise attempt.

        Args:
            user_id: ID of the user.
            exercise_id: ID of the exercise.
            code: Code submitted by the user.
            success: Whether the attempt was successful.
            feedback: Feedback for the attempt.
        """
        if self._connection is None:
            await self.connect()

        # Start a transaction
        await self._connection.execute("BEGIN")
        try:
            # Insert the attempt
            await self._connection.execute(
                """
                INSERT INTO exercise_attempts (
                    user_id, exercise_id, code, success, feedback, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    exercise_id,
                    code,
                    success,
                    feedback,
                    datetime.now().isoformat(),
                ),
            )

            # Commit the transaction
            await self._connection.commit()
        except Exception:
            # Rollback on error
            await self._connection.rollback()
            raise

    async def get_user_progress(self, user_id: str) -> dict[str, Any]:
        """Get a user's progress.

        Args:
            user_id: ID of the user.

        Returns:
            Dictionary with progress information.
        """
        if self._connection is None:
            await self.connect()

        # Get completed sections
        completed_sections = []
        async with self._connection.execute(
            """
            SELECT tutorial_id, section_id, completed_at
            FROM user_progress
            WHERE user_id = ? AND completed = 1
            """,
            (user_id,),
        ) as cursor:
            async for row in cursor:
                completed_sections.append(
                    {
                        "tutorial_id": row["tutorial_id"],
                        "section_id": row["section_id"],
                        "completed_at": datetime.fromisoformat(row["completed_at"]),
                    }
                )

        # Get exercise attempts
        exercise_attempts = []
        async with self._connection.execute(
            """
            SELECT exercise_id, success, created_at
            FROM exercise_attempts
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ) as cursor:
            async for row in cursor:
                exercise_attempts.append(
                    {
                        "exercise_id": row["exercise_id"],
                        "success": bool(row["success"]),
                        "created_at": datetime.fromisoformat(row["created_at"]),
                    }
                )

        # Calculate statistics
        total_sections = await self._connection.execute("SELECT COUNT(*) FROM tutorial_sections")
        total_sections = await total_sections.fetchone()
        total_sections = total_sections[0] if total_sections else 0

        total_exercises = await self._connection.execute("SELECT COUNT(*) FROM exercises")
        total_exercises = await total_exercises.fetchone()
        total_exercises = total_exercises[0] if total_exercises else 0

        completed_exercise_count = len({attempt["exercise_id"] for attempt in exercise_attempts if attempt["success"]})

        return {
            "user_id": user_id,
            "completed_sections": completed_sections,
            "exercise_attempts": exercise_attempts,
            "total_sections": total_sections,
            "completed_section_count": len(completed_sections),
            "section_completion_percentage": (
                len(completed_sections) / total_sections * 100 if total_sections > 0 else 0
            ),
            "total_exercises": total_exercises,
            "completed_exercise_count": completed_exercise_count,
            "exercise_completion_percentage": (
                completed_exercise_count / total_exercises * 100 if total_exercises > 0 else 0
            ),
        }
