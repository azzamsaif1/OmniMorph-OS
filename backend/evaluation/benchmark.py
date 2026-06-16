"""Benchmark — Anonymous Expert Comparison (Feature 12).

Compares a user's performance to aggregated expert baselines without
revealing individual identities. Generates personalized challenges to
close skill gaps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkResult:
    """Result of comparing a user against the expert baseline."""

    dimension: str
    user_score: float
    expert_p50: float
    expert_p90: float
    percentile: float
    gap: float
    challenge_hint: str


# Simulated expert baselines (in production these come from aggregated P2P data)
_EXPERT_BASELINES: dict[str, dict[str, float]] = {
    "learning_speed": {"p50": 0.60, "p90": 0.88},
    "engineering_depth": {"p50": 0.55, "p90": 0.85},
    "execution_capability": {"p50": 0.58, "p90": 0.82},
    "continuous_evolution": {"p50": 0.50, "p90": 0.80},
    "integration_quality": {"p50": 0.52, "p90": 0.78},
}

_CHALLENGE_TEMPLATES: dict[str, str] = {
    "learning_speed": "Try implementing a new pattern you've never used before in under 30 minutes.",
    "engineering_depth": "Solve a distributed systems problem requiring consensus algorithms.",
    "execution_capability": "Complete a full feature (with tests) in a single focused session.",
    "continuous_evolution": "Refactor a module you wrote 3 months ago with your current knowledge.",
    "integration_quality": "Build a service that connects three previously unrelated subsystems.",
}


class BenchmarkEngine:
    """Compares user capability profiles against expert baselines."""

    def compare(
        self, user_scores: dict[str, float]
    ) -> list[BenchmarkResult]:
        """Compare user dimension scores against expert baselines.

        Args:
            user_scores: Mapping of dimension name → user score (0.0–1.0).

        Returns:
            List of BenchmarkResult per dimension.
        """
        results: list[BenchmarkResult] = []
        for dim, score in user_scores.items():
            baseline = _EXPERT_BASELINES.get(dim)
            if not baseline:
                continue
            p50 = baseline["p50"]
            p90 = baseline["p90"]
            percentile = _estimate_percentile(score, p50, p90)
            gap = max(0.0, p50 - score)
            results.append(
                BenchmarkResult(
                    dimension=dim,
                    user_score=round(score, 4),
                    expert_p50=p50,
                    expert_p90=p90,
                    percentile=round(percentile, 1),
                    gap=round(gap, 4),
                    challenge_hint=_CHALLENGE_TEMPLATES.get(dim, ""),
                )
            )
        return results

    def generate_challenges(
        self, user_scores: dict[str, float], count: int = 3
    ) -> list[dict[str, Any]]:
        """Generate personalized challenges targeting the weakest dimensions."""
        results = self.compare(user_scores)
        # Sort by gap descending (biggest weaknesses first)
        results.sort(key=lambda r: r.gap, reverse=True)
        challenges: list[dict[str, Any]] = []
        for r in results[:count]:
            challenges.append(
                {
                    "dimension": r.dimension,
                    "current_score": r.user_score,
                    "target_score": r.expert_p50,
                    "gap": r.gap,
                    "challenge": r.challenge_hint,
                    "difficulty": "advanced" if r.gap > 0.2 else "moderate",
                }
            )
        return challenges


def _estimate_percentile(score: float, p50: float, p90: float) -> float:
    """Rough percentile estimate assuming normal-ish distribution."""
    if score >= p90:
        return 90.0 + 10.0 * min((score - p90) / (1.0 - p90 + 1e-9), 1.0)
    if score >= p50:
        return 50.0 + 40.0 * (score - p50) / (p90 - p50 + 1e-9)
    return 50.0 * score / (p50 + 1e-9)
