"""Interface Supervisor — coordinates UI mode transitions.

Reads the adaptation plan and ensures the frontend receives the correct
mode, theme, and interaction parameters.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log


class InterfaceAgent(BaseAgent):
    """Translates the adaptation plan into frontend directives."""

    def __init__(self) -> None:
        super().__init__(AgentRole.INTERFACE)

    async def process(self, state: AgentState) -> AgentState:
        plan = state.context.get("adaptation_plan", {})
        ui_mode = plan.get("ui_mode", state.ui_mode)
        theme = plan.get("ambient_theme", "default")
        verbosity = plan.get("agent_verbosity", 0.5)

        directive = {
            "ui_mode": ui_mode,
            "theme": theme,
            "verbosity": verbosity,
            "suggestions_enabled": plan.get("suggestions_enabled", True),
            "break_reminder": plan.get("break_reminder", False),
        }
        state.context["ui_directive"] = directive
        state.ui_mode = ui_mode

        self._emit(state, f"[Interface] mode={ui_mode} theme={theme}")
        log.debug("interface_agent.processed", mode=ui_mode, theme=theme)
        return state
