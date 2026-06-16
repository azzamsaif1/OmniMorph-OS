"""Capability Index — 5-Dimensional Adaptive Scoring.

Measures user growth across five dimensions:
  1. Learning Speed — how quickly new concepts are absorbed
  2. Engineering Depth — complexity of problems solved
  3. Execution Capability — throughput and quality of output
  4. Continuous Evolution — improvement trajectory over time
  5. Integration Quality — ability to combine disparate skills

Each dimension is scored 0.0–1.0; the composite index is a weighted average.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DimensionScore:
    """Score for a single capability dimension."""

    name: str
    value: float = 0.0
    samples: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update(self, observation: float, alpha: float = 0.1) -> None:
        """Exponential moving average update."""
        self.value = alpha * observation + (1 - alpha) * self.value
        self.samples += 1
        self.last_updated = datetime.now(timezone.utc)


@dataclass
class CapabilityProfile:
    """Complete 5-dimensional capability profile for a user."""

    user_id: str
    learning_speed: DimensionScore = field(
        default_factory=lambda: DimensionScore(name="learning_speed")
    )
    engineering_depth: DimensionScore = field(
        default_factory=lambda: DimensionScore(name="engineering_depth")
    )
    execution_capability: DimensionScore = field(
        default_factory=lambda: DimensionScore(name="execution_capability")
    )
    continuous_evolution: DimensionScore = field(
        default_factory=lambda: DimensionScore(name="continuous_evolution")
    )
    integration_quality: DimensionScore = field(
        default_factory=lambda: DimensionScore(name="integration_quality")
    )

    @property
    def dimensions(self) -> list[DimensionScore]:
        return [
            self.learning_speed,
            self.engineering_depth,
            self.execution_capability,
            self.continuous_evolution,
            self.integration_quality,
        ]

    @property
    def composite_index(self) -> float:
        """Weighted composite score (equal weights by default)."""
        weights = [0.20, 0.25, 0.20, 0.20, 0.15]
        return sum(w * d.value for w, d in zip(weights, self.dimensions))

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "composite_index": round(self.composite_index, 4),
            "dimensions": {
                d.name: {"value": round(d.value, 4), "samples": d.samples}
                for d in self.dimensions
            },
        }


class CapabilityIndexEngine:
    """Manages capability profiles and processes skill observations."""

    def __init__(self) -> None:
        self._profiles: dict[str, CapabilityProfile] = {}

    def get_or_create(self, user_id: str) -> CapabilityProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = CapabilityProfile(user_id=user_id)
        return self._profiles[user_id]

    def record_observation(
        self,
        user_id: str,
        dimension: str,
        value: float,
    ) -> CapabilityProfile:
        """Record a capability observation for a user.

        Args:
            user_id: Unique user identifier.
            dimension: One of the five dimension names.
            value: Observed score (0.0–1.0).

        Returns:
            Updated CapabilityProfile.
        """
        profile = self.get_or_create(user_id)
        dim_map = {d.name: d for d in profile.dimensions}
        if dimension in dim_map:
            dim_map[dimension].update(min(max(value, 0.0), 1.0))
        return profile

    def evaluate_growth(self, user_id: str) -> dict[str, Any]:
        """Evaluate growth trajectory for a user."""
        profile = self.get_or_create(user_id)
        return {
            "user_id": user_id,
            "composite_index": round(profile.composite_index, 4),
            "maturity_level": _maturity_label(profile.composite_index),
            "dimensions": {
                d.name: {"value": round(d.value, 4), "samples": d.samples}
                for d in profile.dimensions
            },
        }


def _maturity_label(index: float) -> str:
    if index >= 0.85:
        return "expert"
    if index >= 0.65:
        return "advanced"
    if index >= 0.40:
        return "intermediate"
    if index >= 0.20:
        return "developing"
    return "novice"
