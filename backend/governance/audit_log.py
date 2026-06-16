"""Audit Log — Immutable Action Trail.

Records every significant system action with timestamps, actors,
and reasoning. Designed to be append-only for regulatory compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AuditCategory(str, Enum):
    """Categories of auditable events."""

    DATA_ACCESS = "data_access"
    AGENT_DECISION = "agent_decision"
    PRIVACY_ACTION = "privacy_action"
    USER_CONSENT = "user_consent"
    SYSTEM_CONFIG = "system_config"
    SECURITY_EVENT = "security_event"
    SKILL_SHARE = "skill_share"


@dataclass
class AuditEntry:
    """A single entry in the immutable audit log."""

    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    category: AuditCategory = AuditCategory.AGENT_DECISION
    actor: str = "system"  # who performed the action
    action: str = ""  # what was done
    target: str = ""  # what was affected
    reasoning: str = ""  # why (for agent decisions)
    metadata: dict[str, Any] = field(default_factory=dict)
    outcome: str = "success"  # "success", "denied", "error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "outcome": self.outcome,
        }


class AuditLog:
    """Append-only audit log for UCSK system actions.

    In production, this would write to an immutable store (e.g., PostgreSQL
    with append-only constraints, or a dedicated audit DB). For the scaffold,
    entries are stored in memory with the same interface.
    """

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(
        self,
        category: AuditCategory,
        actor: str,
        action: str,
        target: str = "",
        reasoning: str = "",
        metadata: dict[str, Any] | None = None,
        outcome: str = "success",
    ) -> AuditEntry:
        """Record an action in the audit log (append-only).

        Args:
            category: Type of auditable event.
            actor: Who performed the action (user_id, agent_name, "system").
            action: Description of what was done.
            target: What resource/entity was affected.
            reasoning: Why the action was taken (for agent decisions).
            metadata: Additional context.
            outcome: Result of the action.

        Returns:
            The created AuditEntry.
        """
        entry = AuditEntry(
            category=category,
            actor=actor,
            action=action,
            target=target,
            reasoning=reasoning,
            metadata=metadata or {},
            outcome=outcome,
        )
        self._entries.append(entry)
        return entry

    def query(
        self,
        category: AuditCategory | None = None,
        actor: str | None = None,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """Query audit log entries with optional filters.

        Args:
            category: Filter by category.
            actor: Filter by actor.
            limit: Maximum entries to return.

        Returns:
            List of matching entries (most recent first).
        """
        results = self._entries
        if category:
            results = [e for e in results if e.category == category]
        if actor:
            results = [e for e in results if e.actor == actor]
        return list(reversed(results[-limit:]))

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def export(self, limit: int = 100) -> list[dict[str, Any]]:
        """Export recent audit entries as serializable dicts."""
        return [e.to_dict() for e in reversed(self._entries[-limit:])]
