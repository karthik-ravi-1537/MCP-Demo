"""Tutorial content renderer."""

import re

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from .models import CodeExample, Exercise, Tutorial, TutorialSection


class TutorialRenderer:
    """Renderer for tutorial content."""

    def __init__(self, highlight_style: str = "default"):
        """Initialize the renderer.

        Args:
            highlight_style: Pygments style for syntax highlighting.
        """
        self.highlight_style = highlight_style
        self.html_formatter = HtmlFormatter(style=highlight_style)

        # Initialize Markdown extensions
        self.markdown_extensions = [
            "fenced_code",
            "codehilite",
            "tables",
            "nl2br",
        ]

    def render_tutorial(self, tutorial: Tutorial) -> dict[str, str | list[dict]]:
        """Render a tutorial to HTML.

        Args:
            tutorial: The tutorial to render.

        Returns:
            Dictionary with rendered content.
        """
        sections = []

        for section in tutorial.sections:
            sections.append(self.render_section(section))

        return {
            "id": tutorial.id,
            "title": tutorial.title,
            "description": markdown.markdown(tutorial.description, extensions=self.markdown_extensions),
            "level": tutorial.level.value,
            "prerequisites": tutorial.prerequisites,
            "estimated_time": tutorial.estimated_time,
            "sections": sections,
        }

    def render_section(self, section: TutorialSection) -> dict[str, str | list[dict]]:
        """Render a tutorial section to HTML.

        Args:
            section: The section to render.

        Returns:
            Dictionary with rendered content.
        """
        # Process the content to handle special blocks
        processed_content = self._process_content(section.content)

        # Render the content to HTML
        html_content = markdown.markdown(processed_content, extensions=self.markdown_extensions)

        # Render code examples
        code_examples = []
        for example in section.code_examples:
            code_examples.append(self.render_code_example(example))

        # Render exercises
        exercises = []
        for exercise in section.exercises:
            exercises.append(self.render_exercise(exercise))

        return {
            "id": section.id,
            "title": section.title,
            "content": html_content,
            "code_examples": code_examples,
            "exercises": exercises,
        }

    def render_code_example(self, example: CodeExample) -> dict[str, str]:
        """Render a code example to HTML.

        Args:
            example: The code example to render.

        Returns:
            Dictionary with rendered content.
        """
        # Highlight the code
        highlighted_code = self._highlight_code(example.code, example.language)

        return {
            "id": example.id,
            "title": example.title,
            "description": markdown.markdown(example.description, extensions=self.markdown_extensions),
            "code": example.code,
            "highlighted_code": highlighted_code,
            "language": example.language,
            "expected_output": example.expected_output,
        }

    def render_exercise(self, exercise: Exercise) -> dict[str, str | list[dict]]:
        """Render an exercise to HTML.

        Args:
            exercise: The exercise to render.

        Returns:
            Dictionary with rendered content.
        """
        # Highlight the starter code
        highlighted_starter_code = self._highlight_code(exercise.starter_code, "python")  # Assuming Python for now

        return {
            "id": exercise.id,
            "title": exercise.title,
            "description": markdown.markdown(exercise.description, extensions=self.markdown_extensions),
            "difficulty": exercise.difficulty.value,
            "starter_code": exercise.starter_code,
            "highlighted_starter_code": highlighted_starter_code,
            "test_cases": exercise.test_cases,
            "hints": [markdown.markdown(hint, extensions=self.markdown_extensions) for hint in exercise.hints],
            "max_attempts": exercise.max_attempts,
        }

    def _highlight_code(self, code: str, language: str | None = None) -> str:
        """Highlight code using Pygments.

        Args:
            code: The code to highlight.
            language: The language of the code.

        Returns:
            HTML with highlighted code.
        """
        try:
            if language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)

            return highlight(code, lexer, self.html_formatter)

        except ClassNotFound:
            # If the language is not found, use plain text
            return f"<pre><code>{code}</code></pre>"

    def _process_content(self, content: str) -> str:
        """Process tutorial content to handle special blocks.

        Args:
            content: The content to process.

        Returns:
            Processed content.
        """
        # Process interactive code blocks
        content = self._process_interactive_blocks(content)

        # Process note blocks
        content = self._process_note_blocks(content)

        # Process warning blocks
        content = self._process_warning_blocks(content)

        # Process tip blocks
        content = self._process_tip_blocks(content)

        return content

    def _process_interactive_blocks(self, content: str) -> str:
        """Process interactive code blocks.

        Args:
            content: The content to process.

        Returns:
            Processed content.
        """
        # Match blocks like:
        # ```interactive python
        # print("Hello, world!")
        # ```
        pattern = r"```interactive\s+(\w+)\s*\n(.*?)```"

        def replace(match):
            language = match.group(1)
            code = match.group(2)

            # Create an interactive code block
            return f"""
<div class="interactive-code" data-language="{language}">
<pre><code>{code}</code></pre>
<button class="run-button">Run</button>
<div class="output"></div>
</div>
"""

        return re.sub(pattern, replace, content, flags=re.DOTALL)

    def _process_note_blocks(self, content: str) -> str:
        """Process note blocks.

        Args:
            content: The content to process.

        Returns:
            Processed content.
        """
        # Match blocks like:
        # ::: note
        # This is a note.
        # :::
        pattern = r":::\s*note\s*\n(.*?):::"

        def replace(match):
            note_content = match.group(1)

            # Create a note block
            return f"""
<div class="note">
<div class="note-header">Note</div>
<div class="note-content">

{note_content}

</div>
</div>
"""

        return re.sub(pattern, replace, content, flags=re.DOTALL)

    def _process_warning_blocks(self, content: str) -> str:
        """Process warning blocks.

        Args:
            content: The content to process.

        Returns:
            Processed content.
        """
        # Match blocks like:
        # ::: warning
        # This is a warning.
        # :::
        pattern = r":::\s*warning\s*\n(.*?):::"

        def replace(match):
            warning_content = match.group(1)

            # Create a warning block
            return f"""
<div class="warning">
<div class="warning-header">Warning</div>
<div class="warning-content">

{warning_content}

</div>
</div>
"""

        return re.sub(pattern, replace, content, flags=re.DOTALL)

    def _process_tip_blocks(self, content: str) -> str:
        """Process tip blocks.

        Args:
            content: The content to process.

        Returns:
            Processed content.
        """
        # Match blocks like:
        # ::: tip
        # This is a tip.
        # :::
        pattern = r":::\s*tip\s*\n(.*?):::"

        def replace(match):
            tip_content = match.group(1)

            # Create a tip block
            return f"""
<div class="tip">
<div class="tip-header">Tip</div>
<div class="tip-content">

{tip_content}

</div>
</div>
"""

        return re.sub(pattern, replace, content, flags=re.DOTALL)

    def get_css(self) -> str:
        """Get CSS for syntax highlighting and custom blocks.

        Returns:
            CSS string.
        """
        # Get Pygments CSS
        pygments_css = self.html_formatter.get_style_defs(".codehilite")

        # Add custom CSS
        custom_css = """
/* Tutorial styles */
.tutorial-section {
    margin-bottom: 2rem;
}

.tutorial-section h2 {
    margin-top: 2rem;
    margin-bottom: 1rem;
}

/* Code example styles */
.code-example {
    margin-bottom: 1.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
}

.code-example-header {
    background-color: #f5f5f5;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
}

.code-example-description {
    padding: 1rem;
    background-color: #fff;
}

.code-example-code {
    padding: 1rem;
    background-color: #f8f8f8;
    overflow-x: auto;
}

/* Exercise styles */
.exercise {
    margin-bottom: 2rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
}

.exercise-header {
    background-color: #f0f0f0;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.exercise-difficulty {
    font-size: 0.8rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background-color: #eee;
}

.exercise-difficulty.beginner {
    background-color: #d4edda;
    color: #155724;
}

.exercise-difficulty.intermediate {
    background-color: #fff3cd;
    color: #856404;
}

.exercise-difficulty.advanced {
    background-color: #f8d7da;
    color: #721c24;
}

.exercise-description {
    padding: 1rem;
    background-color: #fff;
}

.exercise-code {
    padding: 1rem;
    background-color: #f8f8f8;
    overflow-x: auto;
}

.exercise-hints {
    padding: 1rem;
    background-color: #f0f0f0;
    border-top: 1px solid #ddd;
}

.exercise-hint {
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* Interactive code block styles */
.interactive-code {
    margin-bottom: 1.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
}

.interactive-code pre {
    margin: 0;
    padding: 1rem;
    background-color: #f8f8f8;
    overflow-x: auto;
}

.interactive-code .run-button {
    display: block;
    width: 100%;
    padding: 0.5rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
}

.interactive-code .run-button:hover {
    background-color: #45a049;
}

.interactive-code .output {
    padding: 1rem;
    background-color: #f0f0f0;
    border-top: 1px solid #ddd;
    white-space: pre-wrap;
    font-family: monospace;
    min-height: 1.5rem;
}

/* Note, warning, and tip block styles */
.note, .warning, .tip {
    margin: 1.5rem 0;
    padding: 1rem;
    border-radius: 4px;
}

.note {
    background-color: #e7f3fe;
    border-left: 4px solid #2196F3;
}

.warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}

.tip {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
}

.note-header, .warning-header, .tip-header {
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.note-header {
    color: #0c5460;
}

.warning-header {
    color: #856404;
}

.tip-header {
    color: #155724;
}
"""

        return pygments_css + custom_css
