"""Code Review Specialist — automated review and style enforcement.

Analyses diffs, suggests refactors, flags anti-patterns, and checks
adherence to project style guides.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
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
            issues: list[str] = []

            # Simple heuristic checks (real impl uses Gemini / AST)
            lines = code.split("\n") if code else []
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    issues.append(f"Line {i}: exceeds 120 chars")
                if "TODO" in line:
                    issues.append(f"Line {i}: unresolved TODO")
                if "import *" in line:
                    issues.append(f"Line {i}: wildcard import")

            task["status"] = "done"
            task["result"] = issues
            self._emit(
                state,
                f"[CodeReview] {len(issues)} issue(s) found",
            )
            state.completed_tasks.append(task)

        log.debug("codereview_agent.processed", tasks=len(tasks))
        return state
