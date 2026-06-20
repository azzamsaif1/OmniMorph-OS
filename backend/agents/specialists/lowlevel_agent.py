"""Low-Level Specialist — handles systems programming concerns.

Assists with memory management, concurrency, OS-level interactions,
and performance-critical code paths. Uses Gemini for analysis.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_analyze_code
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
            code = task.get("code", "")
            desc = task.get("description", "N/A")

            if code:
                analysis = await gemini_analyze_code(
                    code=code,
                    task=f"low-level systems review: {desc}. "
                    "Focus on memory safety, concurrency bugs, race conditions, "
                    "deadlocks, resource leaks, and performance bottlenecks.",
                    language=task.get("language", "python"),
                )
                result = (
                    f"Low-level review for '{desc}': "
                    f"{len(analysis.get('issues', []))} concerns. "
                    f"{analysis.get('summary', '')}"
                )
                task["analysis"] = analysis
            else:
                result = f"Low-level review for '{desc}' — completed (no code provided)"

            task["status"] = "done"
            task["result"] = result
            self._emit(state, f"[LowLevel] {result}")
            state.completed_tasks.append(task)

        log.debug("lowlevel_agent.processed", tasks=len(tasks))
        return state
