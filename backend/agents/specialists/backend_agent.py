"""Backend Specialist — assists with server-side code tasks.

Analyses backend code (API routes, DB queries, server config) and
suggests improvements, bug fixes, and optimisations using Gemini.
"""

from __future__ import annotations

from typing import Any

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_analyze_code
from backend.utils.logger import log


class BackendAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.BACKEND)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]
        for task in tasks:
            code = task.get("code", "")
            desc = task.get("description", "N/A")

            if code:
                analysis = await gemini_analyze_code(
                    code=code,
                    task=f"Review: {desc}",
                    language=task.get("language", "python"),
                )
                result = (
                    f"Backend analysis for '{desc}': "
                    f"Quality {analysis.get('quality_score', 'N/A')}/100. "
                    f"{len(analysis.get('issues', []))} issues found. "
                    f"{analysis.get('summary', '')}"
                )
                task["analysis"] = analysis
            else:
                result = f"Backend analysis for '{desc}' — completed (no code provided)"

            task["status"] = "done"
            task["result"] = result
            self._emit(state, f"[Backend] {result}")
            state.completed_tasks.append(task)

        log.debug("backend_agent.processed", tasks=len(tasks))
        return state
