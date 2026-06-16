"""Analysis Supervisor — interprets the current code context.

Examines the user's active file, recent actions, and errors to produce
actionable insights for specialist agents.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log


class AnalysisAgent(BaseAgent):
    """Produces a high-level analysis brief from the work context."""

    def __init__(self) -> None:
        super().__init__(AgentRole.ANALYSIS)

    async def process(self, state: AgentState) -> AgentState:
        ctx = state.context.get("work_context", {})
        active = ctx.get("active_file")
        actions = ctx.get("recent_actions", [])

        insights: list[str] = []
        if active:
            insights.append(f"Active file: {active.get('path', '?')} ({active.get('language', '?')})")
        if actions:
            last = actions[-1] if actions else {}
            insights.append(f"Last action: {last.get('action', '?')}")

        error_actions = [a for a in actions if "error" in a.get("action", "").lower()]
        if error_actions:
            insights.append(f"Recent errors: {len(error_actions)}")

        brief = " | ".join(insights) if insights else "No context available"
        self._emit(state, f"[Analysis] {brief}")
        state.context["analysis_brief"] = brief
        log.debug("analysis_agent.processed", brief=brief)
        return state
