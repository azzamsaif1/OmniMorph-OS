"""Competitive Engineering Twin — AI clone that competes with the user (Feature 7).

Creates a virtual competitor calibrated to the user's skill level.
The twin solves the same problems slightly faster/better to push
the user beyond their limits via healthy competition.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any

from backend.config import settings
from backend.utils.logger import log


@dataclass
class ChallengeResult:
    """Result of a competitive challenge round."""

    challenge_id: str
    user_score: float
    twin_score: float
    user_time_sec: float
    twin_time_sec: float
    domain: str
    difficulty: str
    winner: str  # "user", "twin", "tie"
    feedback: str


@dataclass
class CompetitorProfile:
    """The twin's calibrated skill profile."""

    user_id: str
    twin_level: float = 0.6
    win_rate: float = 0.45  # starts slightly below 50% to encourage
    total_rounds: int = 0
    user_wins: int = 0
    twin_wins: int = 0
    streak: int = 0
    calibration_history: list[float] = field(default_factory=list)


class CompetitiveTwinEngine:
    """Manages the competitive engineering twin for each user."""

    def __init__(self) -> None:
        self._profiles: dict[str, CompetitorProfile] = {}

    def get_profile(self, user_id: str) -> CompetitorProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = CompetitorProfile(user_id=user_id)
        return self._profiles[user_id]

    async def generate_challenge(
        self,
        user_id: str,
        domain: str = "backend",
        difficulty: str = "auto",
    ) -> dict[str, Any]:
        """Generate a head-to-head coding challenge."""
        profile = self.get_profile(user_id)

        if difficulty == "auto":
            difficulty = self._auto_difficulty(profile)

        challenge_templates = {
            "easy": [
                {"title": "Reverse a Linked List", "time_limit": 300},
                {"title": "Implement Binary Search", "time_limit": 240},
                {"title": "Build a Stack with Min Operation", "time_limit": 360},
            ],
            "medium": [
                {"title": "Design a LRU Cache", "time_limit": 600},
                {"title": "Implement a Rate Limiter", "time_limit": 720},
                {"title": "Build a Thread-Safe Queue", "time_limit": 540},
            ],
            "hard": [
                {"title": "Implement Raft Leader Election", "time_limit": 1200},
                {"title": "Build a B-Tree Index", "time_limit": 1500},
                {"title": "Design an Event Sourcing Framework", "time_limit": 1800},
            ],
            "expert": [
                {"title": "Implement a Distributed Lock Manager", "time_limit": 2400},
                {"title": "Build a Query Optimizer", "time_limit": 3000},
                {"title": "Create a CRDT Library", "time_limit": 2700},
            ],
        }

        templates = challenge_templates.get(difficulty, challenge_templates["medium"])
        template = random.choice(templates)

        twin_est = self._estimate_twin_time(profile, template["time_limit"])

        return {
            "challenge_id": f"ch_{int(time.time())}_{user_id[:6]}",
            "title": template["title"],
            "domain": domain,
            "difficulty": difficulty,
            "time_limit_sec": template["time_limit"],
            "twin_estimated_time": twin_est,
            "twin_level": round(profile.twin_level, 2),
            "your_streak": profile.streak,
            "twin_message": self._twin_taunt(profile),
        }

    async def submit_result(
        self,
        user_id: str,
        challenge_id: str,
        user_score: float,
        user_time: float,
        domain: str = "backend",
        difficulty: str = "medium",
    ) -> ChallengeResult:
        """Submit user's result and simulate the twin's performance."""
        profile = self.get_profile(user_id)

        twin_score = self._simulate_twin_score(profile, user_score)
        twin_time = self._simulate_twin_time(profile, user_time)

        if user_score > twin_score:
            winner = "user"
            profile.user_wins += 1
            profile.streak = max(0, profile.streak) + 1
            feedback = "You outperformed your twin. The bar has been raised."
        elif twin_score > user_score:
            winner = "twin"
            profile.twin_wins += 1
            profile.streak = min(0, profile.streak) - 1
            feedback = "Your twin edged you out. Analyze the approach difference."
        else:
            winner = "tie"
            feedback = "A tie. You're evenly matched at this level."

        profile.total_rounds += 1
        self._recalibrate(profile, user_score)

        result = ChallengeResult(
            challenge_id=challenge_id,
            user_score=user_score,
            twin_score=twin_score,
            user_time_sec=user_time,
            twin_time_sec=twin_time,
            domain=domain,
            difficulty=difficulty,
            winner=winner,
            feedback=feedback,
        )
        log.info(
            "competitive_twin.result",
            user=user_id,
            winner=winner,
            user_score=user_score,
            twin_score=twin_score,
        )
        return result

    def get_stats(self, user_id: str) -> dict[str, Any]:
        p = self.get_profile(user_id)
        return {
            "total_rounds": p.total_rounds,
            "user_wins": p.user_wins,
            "twin_wins": p.twin_wins,
            "ties": p.total_rounds - p.user_wins - p.twin_wins,
            "win_rate": p.user_wins / max(p.total_rounds, 1),
            "current_streak": p.streak,
            "twin_level": round(p.twin_level, 3),
        }

    def _auto_difficulty(self, profile: CompetitorProfile) -> str:
        if profile.twin_level > 0.8:
            return "expert"
        if profile.twin_level > 0.6:
            return "hard"
        if profile.twin_level > 0.35:
            return "medium"
        return "easy"

    def _estimate_twin_time(self, profile: CompetitorProfile, limit: int) -> float:
        base = limit * (1.0 - profile.twin_level * 0.4)
        jitter = random.uniform(-0.1, 0.1) * base
        return max(60, base + jitter)

    def _simulate_twin_score(self, profile: CompetitorProfile, user_score: float) -> float:
        target = user_score * (0.9 + profile.twin_level * 0.2)
        noise = random.gauss(0, 0.05)
        return max(0.0, min(1.0, target + noise))

    def _simulate_twin_time(self, profile: CompetitorProfile, user_time: float) -> float:
        factor = 1.0 - profile.twin_level * 0.3
        noise = random.gauss(0, 0.1) * user_time
        return max(30, user_time * factor + noise)

    def _recalibrate(self, profile: CompetitorProfile, user_score: float) -> None:
        alpha = 0.1
        profile.twin_level = alpha * user_score + (1 - alpha) * profile.twin_level
        profile.calibration_history.append(profile.twin_level)
        if len(profile.calibration_history) > 100:
            profile.calibration_history = profile.calibration_history[-50:]

    def _twin_taunt(self, profile: CompetitorProfile) -> str:
        if profile.streak >= 3:
            return "Impressive streak. Let's see if you can maintain it."
        if profile.streak <= -3:
            return "I've been winning too much. Time to show me what you've got."
        if profile.total_rounds == 0:
            return "First challenge. Let's see what you're made of."
        return "Ready for another round?"
