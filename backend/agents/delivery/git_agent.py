"""Git agent — version control management for automated delivery.

Handles commit, push, branching, and PR creation.
"""

import subprocess
import time
from pathlib import Path
from typing import Any

from backend.gemini_client import generate_content


class GitAgent:
    """Automated git operations for the delivery pipeline.

    Capabilities:
    - Commit message generation
    - Branch management
    - Conflict detection
    - PR description generation
    - Version tagging
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.operations_completed: int = 0

    async def generate_commit_message(self, diff_summary: str) -> dict[str, Any]:
        """Generate a conventional commit message from diff."""
        prompt = (
            f"Generate a conventional commit message for this change:\n\n"
            f"{diff_summary[:2000]}\n\n"
            f"Use format: type(scope): description\n"
            f"Types: feat, fix, docs, refactor, test, chore"
        )

        message = await generate_content(prompt)
        self.operations_completed += 1

        return {
            "message": message or f"chore: update ({diff_summary[:50]})",
            "generated_at": time.time(),
        }

    def get_status(self) -> dict[str, Any]:
        """Get current git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True,
                cwd=self.repo_path, timeout=10
            )
            files = [l.strip() for l in result.stdout.split("\n") if l.strip()]

            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True,
                cwd=self.repo_path, timeout=10
            )

            return {
                "branch": branch.stdout.strip(),
                "modified_files": len(files),
                "files": files[:20],
                "clean": len(files) == 0,
            }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"error": str(e)}

    def get_diff_summary(self) -> str:
        """Get summary of current changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True, text=True,
                cwd=self.repo_path, timeout=10
            )
            return result.stdout[:2000]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""

    async def generate_pr_description(
        self, branch_name: str, changes_summary: str
    ) -> dict[str, Any]:
        """Generate PR description from branch changes."""
        prompt = (
            f"Generate a pull request description:\n\n"
            f"Branch: {branch_name}\n"
            f"Changes: {changes_summary}\n\n"
            f"Include: summary, changes list, testing done, screenshots needed."
        )

        description = await generate_content(prompt)

        return {
            "branch": branch_name,
            "description": description or f"## Changes\n\n{changes_summary}",
            "generated_at": time.time(),
        }

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "git",
            "operations_completed": self.operations_completed,
            "repo_path": str(self.repo_path),
        }
