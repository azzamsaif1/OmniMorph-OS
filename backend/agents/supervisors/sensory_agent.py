"""Sensory Supervisor — aggregates raw sensing data for downstream agents."""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log


class SensoryAgent(BaseAgent):
    """Reads the latest mental-state from context and broadcasts a summary."""

    def __init__(self) -> None:
        super().__init__(AgentRole.SENSORY)

    async def process(self, state: AgentState) -> AgentState:
        ms = state.context.get("mental_state_snapshot")
        if ms is None:
            return state

        summary = (
            f"[Sensory] State={ms.get('state', 'unknown')} "
            f"confidence={ms.get('confidence', 0):.2f} "
            f"focus={ms.get('focus_score', 0):.2f} "
            f"fatigue={ms.get('fatigue_score', 0):.2f}"
        )
        self._emit(state, summary)
        state.context["sensory_summary"] = summary
        log.debug("sensory_agent.processed", state=ms.get("state"))
        return state
