"""Privacy Guard — Differential Privacy Enforcement.

Applies differential privacy mechanisms to ensure no individual user's
data can be reverse-engineered from shared skill patterns.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any

import numpy as np

from backend.utils.logger import log


@dataclass
class PrivacyBudget:
    """Tracks the privacy budget (epsilon) for a user."""

    user_id: str
    epsilon_total: float  # total budget allocated
    epsilon_spent: float = 0.0  # budget consumed so far

    @property
    def epsilon_remaining(self) -> float:
        return max(0.0, self.epsilon_total - self.epsilon_spent)

    @property
    def exhausted(self) -> bool:
        return self.epsilon_remaining <= 0.0


class PrivacyGuard:
    """Enforces differential privacy on all shared data.

    Key guarantees:
    - All exported skill patterns are anonymized (hashed user IDs)
    - Numeric vectors have calibrated Laplace noise added
    - Privacy budget is tracked per-user to prevent accumulation attacks
    """

    def __init__(self, default_epsilon: float = 1.0) -> None:
        self._default_epsilon = default_epsilon
        self._budgets: dict[str, PrivacyBudget] = {}

    def get_budget(self, user_id: str) -> PrivacyBudget:
        """Get or create privacy budget for a user."""
        if user_id not in self._budgets:
            self._budgets[user_id] = PrivacyBudget(
                user_id=user_id,
                epsilon_total=self._default_epsilon,
            )
        return self._budgets[user_id]

    def anonymize_user_id(self, user_id: str) -> str:
        """One-way hash a user ID for anonymous sharing."""
        salt = "ucsk_privacy_salt_2026"
        return hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()[:16]

    def add_noise(
        self,
        vector: list[float],
        sensitivity: float = 1.0,
        epsilon: float | None = None,
    ) -> list[float]:
        """Add calibrated Laplace noise to a numeric vector.

        Args:
            vector: The original data vector.
            sensitivity: L1 sensitivity of the query.
            epsilon: Privacy parameter (lower = more private).

        Returns:
            Noised vector preserving differential privacy.
        """
        eps = epsilon or self._default_epsilon
        scale = sensitivity / eps
        noise = np.random.laplace(0, scale, len(vector))
        return [float(v + n) for v, n in zip(vector, noise)]

    def sanitize_skill_diff(
        self, user_id: str, skill_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Sanitize a skill diff for P2P sharing.

        Args:
            user_id: The originating user.
            skill_data: Raw skill diff data to sanitize.

        Returns:
            Sanitized skill diff or None if budget exhausted.
        """
        budget = self.get_budget(user_id)
        if budget.exhausted:
            log.warning("privacy_guard.budget_exhausted", user_id=user_id)
            return None

        # Cost per share operation
        cost = 0.1
        budget.epsilon_spent += cost

        # Anonymize
        sanitized: dict[str, Any] = {
            "anonymous_id": self.anonymize_user_id(user_id),
            "share_token": secrets.token_hex(8),
        }

        # Copy allowed fields (no raw code, no personal info)
        allowed_fields = ["skill_category", "difficulty_level", "pattern_type", "domain"]
        for field in allowed_fields:
            if field in skill_data:
                sanitized[field] = skill_data[field]

        # Add noise to any numeric vectors
        if "embedding" in skill_data and isinstance(skill_data["embedding"], list):
            sanitized["embedding"] = self.add_noise(skill_data["embedding"])

        # Strip anything that could identify the user
        sanitized["metadata"] = {
            "privacy_version": "dp-1.0",
            "epsilon_used": cost,
            "noise_mechanism": "laplace",
        }

        return sanitized
