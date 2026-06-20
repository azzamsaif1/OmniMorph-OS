"""Governance API — audit trail, constitutional rules, privacy management."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.governance.audit_log import AuditCategory, AuditLog
from backend.governance.constitution import Constitution
from backend.governance.privacy_guard import PrivacyGuard

router = APIRouter()

_audit = AuditLog()
_constitution = Constitution()
_privacy = PrivacyGuard(default_epsilon=1.0)


class AuditQuery(BaseModel):
    category: str | None = None
    actor: str | None = None
    limit: int = Field(default=50, ge=1, le=500)


class PrivacySanitizeRequest(BaseModel):
    user_id: str
    skill_data: dict[str, Any]


@router.get("/audit")
async def get_audit_log(
    category: str | None = None,
    actor: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    cat_enum = None
    if category:
        try:
            cat_enum = AuditCategory(category)
        except ValueError:
            pass
    entries = _audit.query(category=cat_enum, actor=actor, limit=limit)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": _audit.entry_count,
    }


@router.get("/audit/export")
async def export_audit(limit: int = 100) -> dict[str, Any]:
    return {
        "entries": _audit.export(limit),
        "total": _audit.entry_count,
    }


@router.get("/constitution")
async def get_constitution() -> dict[str, Any]:
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "violation_type": r.violation_type.value,
                "severity": r.severity,
            }
            for r in _constitution.rules
        ],
        "total_rules": len(_constitution.rules),
    }


@router.post("/constitution/validate")
async def validate_action(action: dict[str, Any]) -> dict[str, Any]:
    result = _constitution.validate_action(action)
    if result.permitted:
        _audit.record(
            category=AuditCategory.AGENT_DECISION,
            actor=action.get("actor", "system"),
            action=action.get("type", "unknown"),
            target=action.get("target", ""),
            outcome="success",
        )
    else:
        _audit.record(
            category=AuditCategory.SECURITY_EVENT,
            actor=action.get("actor", "system"),
            action=action.get("type", "unknown"),
            target=action.get("target", ""),
            outcome="denied",
            reasoning="; ".join(result.violations),
        )
    return result.to_dict()


@router.get("/privacy/budget/{user_id}")
async def get_privacy_budget(user_id: str) -> dict[str, Any]:
    budget = _privacy.get_budget(user_id)
    return {
        "user_id": user_id,
        "epsilon_total": budget.epsilon_total,
        "epsilon_spent": round(budget.epsilon_spent, 4),
        "epsilon_remaining": round(budget.epsilon_remaining, 4),
        "exhausted": budget.exhausted,
    }


@router.post("/privacy/sanitize")
async def sanitize_skill_diff(req: PrivacySanitizeRequest) -> dict[str, Any]:
    result = _privacy.sanitize_skill_diff(req.user_id, req.skill_data)
    if result is None:
        return {"status": "denied", "reason": "Privacy budget exhausted"}
    _audit.record(
        category=AuditCategory.SKILL_SHARE,
        actor=_privacy.anonymize_user_id(req.user_id),
        action="sanitize_skill_diff",
        target=req.skill_data.get("skill_category", "unknown"),
    )
    return {"status": "sanitized", "data": result}
