"""Adaptation Engine — decides UI mode and agent behaviour from state.

Maps each ``CognitiveState`` to a ``UIMode`` and a set of agent-behaviour
adjustments (verbosity, proactiveness, pacing).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.sensing.mental_state import CognitiveState
from backend.utils.logger import log


class UIMode(str, Enum):
    """Available interface modalities."""

    VISUAL = "visual"       # Full Monaco + Three.js
    AUDIO = "audio"         # Voice-only (Web Speech)
    HAPTIC = "haptic"       # Minimal + tactile cues (WebHID)
    MIXED = "mixed"         # Combined visual + audio
    ZERO = "zero"           # Background-only, no UI chrome


@dataclass
class AdaptationPlan:
    """What changes across the system for the current state."""

    ui_mode: UIMode
    agent_verbosity: float       # 0 = silent … 1 = fully verbose
    proactiveness: float         # 0 = reactive only … 1 = full auto-suggest
    pacing: float                # 0 = slow/calm … 1 = rapid-fire
    suggestions_enabled: bool
    break_reminder: bool
    ambient_theme: str           # CSS theme token sent to frontend


# Default mapping: state → plan
_STATE_PLANS: dict[CognitiveState, AdaptationPlan] = {
    CognitiveState.FOCUSED: AdaptationPlan(
        ui_mode=UIMode.VISUAL,
        agent_verbosity=0.3,
        proactiveness=0.4,
        pacing=0.7,
        suggestions_enabled=True,
        break_reminder=False,
        ambient_theme="focus-dark",
    ),
    CognitiveState.FLOW: AdaptationPlan(
        ui_mode=UIMode.ZERO,
        agent_verbosity=0.0,
        proactiveness=0.1,
        pacing=0.9,
        suggestions_enabled=False,
        break_reminder=False,
        ambient_theme="flow-minimal",
    ),
    CognitiveState.DISTRACTED: AdaptationPlan(
        ui_mode=UIMode.MIXED,
        agent_verbosity=0.7,
        proactiveness=0.8,
        pacing=0.4,
        suggestions_enabled=True,
        break_reminder=False,
        ambient_theme="attention-warm",
    ),
    CognitiveState.FATIGUED: AdaptationPlan(
        ui_mode=UIMode.AUDIO,
        agent_verbosity=0.5,
        proactiveness=0.3,
        pacing=0.2,
        suggestions_enabled=True,
        break_reminder=True,
        ambient_theme="rest-calm",
    ),
    CognitiveState.FRUSTRATED: AdaptationPlan(
        ui_mode=UIMode.AUDIO,
        agent_verbosity=0.6,
        proactiveness=0.9,
        pacing=0.3,
        suggestions_enabled=True,
        break_reminder=True,
        ambient_theme="support-gentle",
    ),
    CognitiveState.IDLE: AdaptationPlan(
        ui_mode=UIMode.ZERO,
        agent_verbosity=0.0,
        proactiveness=0.0,
        pacing=0.0,
        suggestions_enabled=False,
        break_reminder=False,
        ambient_theme="idle-dim",
    ),
}


class AdaptationEngine:
    """Stateful engine that produces an ``AdaptationPlan`` per cycle."""

    def __init__(self) -> None:
        self._current_plan: AdaptationPlan = _STATE_PLANS[CognitiveState.FOCUSED]
        self._transition_cooldown: int = 0  # frames to wait before switching

    def decide(self, state: CognitiveState, confidence: float) -> AdaptationPlan:
        """Return the plan for *state*; apply hysteresis to avoid flicker."""
        if self._transition_cooldown > 0:
            self._transition_cooldown -= 1
            return self._current_plan

        if confidence < 0.4:
            # Low confidence — keep current plan
            return self._current_plan

        plan = _STATE_PLANS.get(state, _STATE_PLANS[CognitiveState.FOCUSED])
        if plan.ui_mode != self._current_plan.ui_mode:
            self._transition_cooldown = 5  # ~250 ms at 20 fps sensing
            log.info(
                "adaptation.transition",
                from_mode=self._current_plan.ui_mode.value,
                to_mode=plan.ui_mode.value,
                trigger=state.value,
            )
        self._current_plan = plan
        return plan

    @property
    def current_plan(self) -> AdaptationPlan:
        return self._current_plan
