"""Code review agent — automated review using Gemini API.

Provides comprehensive code review with actionable feedback.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class CodeReviewAgent:
    """Specialized agent for automated code review.

    Capabilities:
    - Code quality assessment
    - Performance review
    - Best practices enforcement
    - Refactoring suggestions
    - Documentation quality
    """

    def __init__(self):
        self.tasks_completed: int = 0
        self.success_rate: float = 0.90

    async def review(
        self, code: str, language: str = "python", focus: str = "general"
    ) -> dict[str, Any]:
        """Perform comprehensive code review."""
        prompt = (
            f"Review this {language} code (focus: {focus}):\n\n"
            f"```{language}\n{code[:4000]}\n```\n\n"
            f"Provide:\n"
            f"1. Overall quality score (1-10)\n"
            f"2. Issues found (categorized by severity)\n"
            f"3. Specific improvement suggestions\n"
            f"4. Refactoring opportunities\n"
            f"5. Good practices already in place"
        )

        response = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "code_review",
            "language": language,
            "focus": focus,
            "review": response or "Code review requires Gemini API",
            "lines_reviewed": code.count("\n") + 1,
            "reviewed_at": time.time(),
        }

    async def suggest_refactoring(self, code: str, language: str = "python") -> dict[str, Any]:
        """Suggest specific refactoring improvements."""
        prompt = (
            f"Suggest refactoring for this {language} code:\n\n"
            f"```{language}\n{code[:3000]}\n```\n\n"
            f"Focus on: DRY, SOLID, readability, testability. "
            f"Provide before/after examples."
        )

        response = await generate_content(prompt)
        self.tasks_completed += 1

        return {
            "type": "refactoring",
            "suggestions": response or "Refactoring analysis requires Gemini API",
            "generated_at": time.time(),
        }

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "code_review",
            "tasks_completed": self.tasks_completed,
            "success_rate": self.success_rate,
        }
