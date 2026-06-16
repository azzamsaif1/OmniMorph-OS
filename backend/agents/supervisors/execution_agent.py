"""Execution Supervisor — dispatches tasks to specialist agents.

Maintains a priority queue of pending tasks and delegates them to the
most appropriate specialist based on task type and current load.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log

_TASK_ROUTING: dict[str, AgentRole] = {
    "code_review": AgentRole.CODEREVIEW,
    "test": AgentRole.TESTING,
    "security_scan": AgentRole.SECURITY,
    "architecture": AgentRole.ARCHITECTURE,
    "deploy": AgentRole.DEVOPS,
    "research": AgentRole.RESEARCH,
    "backend": AgentRole.BACKEND,
    "lowlevel": AgentRole.LOWLEVEL,
}


class ExecutionAgent(BaseAgent):
    """Routes pending tasks to specialist agents."""

    def __init__(self) -> None:
        super().__init__(AgentRole.EXECUTION)

    async def process(self, state: AgentState) -> AgentState:
        if not state.pending_tasks:
            return state

        dispatched: list[dict] = []
        remaining: list[dict] = []

        for task in state.pending_tasks:
            task_type = task.get("type", "")
            target = _TASK_ROUTING.get(task_type)
            if target:
                task["assigned_to"] = target.value
                task["status"] = "dispatched"
                dispatched.append(task)
                self._emit(
                    state,
                    f"[Execution] Dispatched '{task_type}' → {target.value}",
                    recipient=target,
                )
            else:
                remaining.append(task)

        state.pending_tasks = remaining
        state.context.setdefault("dispatched_tasks", []).extend(dispatched)
        log.info("execution_agent.dispatched", count=len(dispatched))
        return state
