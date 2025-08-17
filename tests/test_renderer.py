"""Tests for the tutorial content renderer."""

from datetime import datetime

import pytest

from tutorials.models import (
    CodeExample,
    DifficultyLevel,
    Exercise,
    Tutorial,
    TutorialSection,
)
from tutorials.renderer import TutorialRenderer


@pytest.fixture
def renderer() -> TutorialRenderer:
    """Create a tutorial renderer."""
    return TutorialRenderer()


@pytest.fixture
def sample_tutorial() -> Tutorial:
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
                content="""
# Section 1

This is section 1.

```python
print("Hello, world!")
```

::: note
This is a note.
:::

::: warning
This is a warning.
:::

::: tip
This is a tip.
:::

```interactive python
print("Interactive code")
```
""",
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
                        hints=["Try using print()", "The solution is to print 'Solution'"],
                        max_attempts=3,
                    ),
                ],
            ),
        ],
    )


def test_render_tutorial(renderer: TutorialRenderer, sample_tutorial: Tutorial) -> None:
    """Test rendering a tutorial."""
    # Render the tutorial
    rendered = renderer.render_tutorial(sample_tutorial)

    # Check the rendered tutorial
    assert rendered["id"] == sample_tutorial.id
    assert rendered["title"] == sample_tutorial.title
    assert "<p>A tutorial for testing</p>" in rendered["description"]
    assert rendered["level"] == sample_tutorial.level.value
    assert rendered["prerequisites"] == sample_tutorial.prerequisites
    assert rendered["estimated_time"] == sample_tutorial.estimated_time
    assert len(rendered["sections"]) == 1


def test_render_section(renderer: TutorialRenderer, sample_tutorial: Tutorial) -> None:
    """Test rendering a tutorial section."""
    # Render the section
    rendered = renderer.render_section(sample_tutorial.sections[0])

    # Check the rendered section
    assert rendered["id"] == sample_tutorial.sections[0].id
    assert rendered["title"] == sample_tutorial.sections[0].title
    assert "<h1>Section 1</h1>" in rendered["content"]
    assert "<p>This is section 1.</p>" in rendered["content"]
    assert '<div class="note">' in rendered["content"]
    assert '<div class="warning">' in rendered["content"]
    assert '<div class="tip">' in rendered["content"]
    assert '<div class="interactive-code"' in rendered["content"]
    assert len(rendered["code_examples"]) == 1
    assert len(rendered["exercises"]) == 1


def test_render_code_example(renderer: TutorialRenderer, sample_tutorial: Tutorial) -> None:
    """Test rendering a code example."""
    # Render the code example
    rendered = renderer.render_code_example(sample_tutorial.sections[0].code_examples[0])

    # Check the rendered code example
    assert rendered["id"] == sample_tutorial.sections[0].code_examples[0].id
    assert rendered["title"] == sample_tutorial.sections[0].code_examples[0].title
    assert "<p>This is example 1</p>" in rendered["description"]
    assert rendered["code"] == sample_tutorial.sections[0].code_examples[0].code
    # Check that the highlighted code contains the print statement (HTML encoded)
    assert "print" in rendered["highlighted_code"]
    assert "Hello, world!" in rendered["highlighted_code"]
    assert rendered["language"] == sample_tutorial.sections[0].code_examples[0].language
    assert rendered["expected_output"] == sample_tutorial.sections[0].code_examples[0].expected_output


def test_render_exercise(renderer: TutorialRenderer, sample_tutorial: Tutorial) -> None:
    """Test rendering an exercise."""
    # Render the exercise
    rendered = renderer.render_exercise(sample_tutorial.sections[0].exercises[0])

    # Check the rendered exercise
    assert rendered["id"] == sample_tutorial.sections[0].exercises[0].id
    assert rendered["title"] == sample_tutorial.sections[0].exercises[0].title
    assert "<p>This is exercise 1</p>" in rendered["description"]
    assert rendered["difficulty"] == sample_tutorial.sections[0].exercises[0].difficulty.value
    assert rendered["starter_code"] == sample_tutorial.sections[0].exercises[0].starter_code
    assert "# Write your code here" in rendered["highlighted_starter_code"]
    assert rendered["test_cases"] == sample_tutorial.sections[0].exercises[0].test_cases
    assert len(rendered["hints"]) == 2
    assert "<p>Try using print()</p>" in rendered["hints"][0]
    assert rendered["max_attempts"] == sample_tutorial.sections[0].exercises[0].max_attempts


def test_highlight_code(renderer: TutorialRenderer) -> None:
    """Test code highlighting."""
    # Highlight Python code
    highlighted = renderer._highlight_code("print('Hello, world!')", "python")
    assert "print" in highlighted
    assert "Hello, world!" in highlighted

    # Highlight JavaScript code
    highlighted = renderer._highlight_code("console.log('Hello, world!');", "javascript")
    assert "console" in highlighted
    assert "Hello, world!" in highlighted

    # Highlight code with unknown language
    highlighted = renderer._highlight_code("print('Hello, world!')", "unknown")
    assert "<pre><code>" in highlighted
    assert "print('Hello, world!')" in highlighted


def test_process_content(renderer: TutorialRenderer) -> None:
    """Test content processing."""
    # Process content with interactive code block
    content = """
```interactive python
print("Hello, world!")
```
"""
    processed = renderer._process_content(content)
    assert '<div class="interactive-code"' in processed
    assert 'data-language="python"' in processed
    assert 'print("Hello, world!")' in processed

    # Process content with note block
    content = """
::: note
This is a note.
:::
"""
    processed = renderer._process_content(content)
    assert '<div class="note">' in processed
    assert '<div class="note-header">Note</div>' in processed
    assert "This is a note." in processed

    # Process content with warning block
    content = """
::: warning
This is a warning.
:::
"""
    processed = renderer._process_content(content)
    assert '<div class="warning">' in processed
    assert '<div class="warning-header">Warning</div>' in processed
    assert "This is a warning." in processed

    # Process content with tip block
    content = """
::: tip
This is a tip.
:::
"""
    processed = renderer._process_content(content)
    assert '<div class="tip">' in processed
    assert '<div class="tip-header">Tip</div>' in processed
    assert "This is a tip." in processed


def test_get_css(renderer: TutorialRenderer) -> None:
    """Test getting CSS."""
    css = renderer.get_css()

    # Check that the CSS includes Pygments styles
    assert ".codehilite" in css

    # Check that the CSS includes custom styles
    assert ".tutorial-section" in css
    assert ".code-example" in css
    assert ".exercise" in css
    assert ".interactive-code" in css
    assert ".note" in css
    assert ".warning" in css
    assert ".tip" in css
