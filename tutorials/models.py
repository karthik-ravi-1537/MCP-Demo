"""Data models for tutorials."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Difficulty level for tutorials and exercises."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CodeExample(BaseModel):
    """Code example model."""

    id: str
    title: str
    description: str
    code: str
    language: str = "python"
    expected_output: str | None = None


class Exercise(BaseModel):
    """Exercise model."""

    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    starter_code: str
    solution_code: str
    test_cases: list[dict]
    hints: list[str]
    max_attempts: int = 3


class TutorialSection(BaseModel):
    """Tutorial section model."""

    id: str
    title: str
    content: str
    code_examples: list[CodeExample] = Field(default_factory=list)
    exercises: list[Exercise] = Field(default_factory=list)


class Tutorial(BaseModel):
    """Tutorial model."""

    id: str
    title: str
    description: str
    level: DifficultyLevel
    prerequisites: list[str] = Field(default_factory=list)
    sections: list[TutorialSection] = Field(default_factory=list)
    estimated_time: int  # minutes
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
