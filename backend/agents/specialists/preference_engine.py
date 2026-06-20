"""Preference-based Reinforcement Engine (Feature 16).

Learns from implicit user preferences (code edits, style choices,
suggestion acceptance/rejection) to refine UCSK's behavior over time.
Uses a preference model without requiring explicit user feedback.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from backend.utils.logger import log


@dataclass
class PreferenceSignal:
    """A single observed preference signal."""

    signal_type: str  # "accept", "reject", "modify", "ignore"
    category: str  # "suggestion", "ui_mode", "verbosity", "pacing", "code_style"
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class PreferenceProfile:
    """Learned preference model for a user."""

    user_id: str
    # Category -> preference value (0=dislikes..1=prefers)
    preferences: dict[str, float] = field(default_factory=lambda: {
        "verbose_explanations": 0.5,
        "proactive_suggestions": 0.5,
        "code_completion": 0.7,
        "break_reminders": 0.5,
        "voice_guidance": 0.3,
        "haptic_feedback": 0.3,
        "dark_theme": 0.8,
        "auto_mode_switch": 0.6,
        "competitive_mode": 0.4,
        "research_updates": 0.5,
    })
    # Code style preferences
    code_style: dict[str, str] = field(default_factory=lambda: {
        "indentation": "spaces_4",
        "quote_style": "double",
        "line_length": "88",
        "docstring_style": "google",
    })
    signal_count: int = 0
    last_updated: float = field(default_factory=time.time)


class PreferenceEngine:
    """Learns and applies user preferences via implicit signals."""

    def __init__(self, learning_rate: float = 0.1) -> None:
        self._profiles: dict[str, PreferenceProfile] = {}
        self._signals: dict[str, list[PreferenceSignal]] = defaultdict(list)
        self._lr = learning_rate

    def get_profile(self, user_id: str) -> PreferenceProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = PreferenceProfile(user_id=user_id)
        return self._profiles[user_id]

    def record_signal(
        self,
        user_id: str,
        signal_type: str,
        category: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Record an implicit preference signal."""
        signal = PreferenceSignal(
            signal_type=signal_type,
            category=category,
            context=context or {},
        )
        self._signals[user_id].append(signal)
        if len(self._signals[user_id]) > 1000:
            self._signals[user_id] = self._signals[user_id][-500:]

        profile = self.get_profile(user_id)
        self._update_preference(profile, signal)
        profile.signal_count += 1
        profile.last_updated = time.time()
        log.debug(
            "preference_engine.signal",
            user=user_id,
            signal=signal_type,
            category=category,
        )

    def _update_preference(self, profile: PreferenceProfile, signal: PreferenceSignal) -> None:
        """Update preference based on signal type."""
        reward_map = {
            "accept": 0.1,
            "modify": 0.03,
            "ignore": -0.02,
            "reject": -0.08,
        }
        delta = reward_map.get(signal.signal_type, 0.0) * self._lr

        cat = signal.category
        if cat in profile.preferences:
            old = profile.preferences[cat]
            profile.preferences[cat] = max(0.0, min(1.0, old + delta))

    def get_adapted_config(self, user_id: str) -> dict[str, Any]:
        """Generate an adapted configuration based on learned preferences."""
        profile = self.get_profile(user_id)

        verbosity = profile.preferences.get("verbose_explanations", 0.5)
        proactive = profile.preferences.get("proactive_suggestions", 0.5)

        return {
            "verbosity_level": "high" if verbosity > 0.7 else ("low" if verbosity < 0.3 else "medium"),
            "proactive_suggestions": proactive > 0.5,
            "code_completion_enabled": profile.preferences.get("code_completion", 0.7) > 0.4,
            "break_reminders_enabled": profile.preferences.get("break_reminders", 0.5) > 0.4,
            "voice_guidance_enabled": profile.preferences.get("voice_guidance", 0.3) > 0.5,
            "auto_mode_switch": profile.preferences.get("auto_mode_switch", 0.6) > 0.4,
            "competitive_mode": profile.preferences.get("competitive_mode", 0.4) > 0.5,
            "code_style": profile.code_style,
            "confidence": min(0.5 + profile.signal_count * 0.005, 0.95),
        }

    def should_show_suggestion(self, user_id: str, suggestion_type: str) -> bool:
        """Decide whether to show a specific type of suggestion."""
        profile = self.get_profile(user_id)
        pref = profile.preferences.get(suggestion_type, 0.5)
        return pref > 0.35

    def get_stats(self, user_id: str) -> dict[str, Any]:
        profile = self.get_profile(user_id)
        signals = self._signals.get(user_id, [])
        signal_breakdown: dict[str, int] = {}
        for s in signals[-100:]:
            signal_breakdown[s.signal_type] = signal_breakdown.get(s.signal_type, 0) + 1
        return {
            "total_signals": profile.signal_count,
            "recent_signals": signal_breakdown,
            "preferences": {k: round(v, 3) for k, v in profile.preferences.items()},
            "confidence": min(0.5 + profile.signal_count * 0.005, 0.95),
        }
