"""Low-Level Specialist — handles systems programming concerns.

Assists with memory management, concurrency, OS-level interactions,
and performance-critical code paths.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log


class LowLevelAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.LOWLEVEL)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]
        for task in tasks:
            result = f"Low-level review for '{task.get('description', 'N/A')}' — completed"
            task["status"] = "done"
            task["result"] = result
            self._emit(state, f"[LowLevel] {result}")
            state.completed_tasks.append(task)

        log.debug("lowlevel_agent.processed", tasks=len(tasks))
        return state
