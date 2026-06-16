"""Memory Supervisor — coordinates persistence across all stores.

Decides what to persist (vector, graph, event), triggers memory
consolidation, and surfaces relevant memories for other agents.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log


class MemoryAgent(BaseAgent):
    """Persists state snapshots and retrieves relevant memories."""

    def __init__(self) -> None:
        super().__init__(AgentRole.MEMORY)

    async def process(self, state: AgentState) -> AgentState:
        # Determine what to persist from this cycle
        snapshot = {
            "mental_state": state.mental_state,
            "ui_mode": state.ui_mode,
            "message_count": len(state.messages),
            "pending": len(state.pending_tasks),
            "completed": len(state.completed_tasks),
        }

        state.context.setdefault("memory_queue", []).append(
            {"action": "persist_snapshot", "data": snapshot}
        )

        # Surface relevant past memories (placeholder — real impl hits Qdrant)
        state.context["recalled_memories"] = []

        self._emit(state, f"[Memory] Queued snapshot; recalled 0 memories")
        log.debug("memory_agent.processed", queued=1)
        return state
