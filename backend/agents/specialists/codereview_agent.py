"""Code Review Specialist — automated review and style enforcement.

Analyses diffs, suggests refactors, flags anti-patterns, and checks
adherence to project style guides. Uses Gemini for deep review.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_analyze_code
from backend.utils.logger import log


class CodeReviewAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.CODEREVIEW)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        for task in tasks:
            code = task.get("code", state.context.get("active_code", ""))
            issues: list[dict[str, str]] = []

            issues.extend(self._heuristic_check(code))

            if code:
                gemini_result = await gemini_analyze_code(
                    code=code,
                    task="code_review",
                    language=task.get("language", "python"),
                )
                for issue in gemini_result.get("issues", []):
                    issues.append({
                        "severity": issue.get("severity", "info"),
                        "message": issue.get("message", ""),
                        "line": str(issue.get("line", "")),
                        "source": "gemini",
                    })
                task["quality_score"] = gemini_result.get("quality_score", 70)
                task["suggestions"] = gemini_result.get("suggestions", [])

            task["status"] = "done"
            task["result"] = issues
            self._emit(
                state,
                f"[CodeReview] {len(issues)} issue(s) found",
            )
            state.completed_tasks.append(task)

        log.debug("codereview_agent.processed", tasks=len(tasks))
        return state

    def _heuristic_check(self, code: str) -> list[dict[str, str]]:
        issues: list[dict[str, str]] = []
        if not code:
            return issues
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    "severity": "style",
                    "message": f"Line {i}: exceeds 120 chars ({len(line)})",
                    "source": "heuristic",
                })
            if "TODO" in line or "FIXME" in line or "HACK" in line:
                marker = "TODO" if "TODO" in line else ("FIXME" if "FIXME" in line else "HACK")
                issues.append({
                    "severity": "info",
                    "message": f"Line {i}: unresolved {marker}",
                    "source": "heuristic",
                })
            if "import *" in line:
                issues.append({
                    "severity": "warning",
                    "message": f"Line {i}: wildcard import",
                    "source": "heuristic",
                })
            stripped = line.rstrip()
            if stripped != line:
                pass  # trailing whitespace, minor
        return issues
