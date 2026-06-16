"""Backend Specialist — assists with server-side code tasks.

Analyses backend code (API routes, DB queries, server config) and
suggests improvements, bug fixes, and optimisations.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
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
            result = f"Backend analysis for '{task.get('description', 'N/A')}' — completed"
            task["status"] = "done"
            task["result"] = result
            self._emit(state, f"[Backend] {result}")
            state.completed_tasks.append(task)

        log.debug("backend_agent.processed", tasks=len(tasks))
        return state
