"""Preferences API — implicit preference learning (Feature 16)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.specialists.preference_engine import PreferenceEngine

router = APIRouter()

_engine = PreferenceEngine()


class SignalRequest(BaseModel):
    user_id: str = "default"
    signal_type: str  # accept, reject, modify, ignore
    category: str  # suggestion, ui_mode, verbosity, etc.
    context: dict[str, Any] = {}


@router.post("/signal")
async def record_signal(req: SignalRequest) -> dict[str, str]:
    _engine.record_signal(
        user_id=req.user_id,
        signal_type=req.signal_type,
        category=req.category,
        context=req.context,
    )
    return {"status": "recorded"}


@router.get("/config/{user_id}")
async def get_adapted_config(user_id: str) -> dict[str, Any]:
    return _engine.get_adapted_config(user_id)


@router.get("/stats/{user_id}")
async def get_preference_stats(user_id: str) -> dict[str, Any]:
    return _engine.get_stats(user_id)


@router.get("/should-show/{user_id}/{suggestion_type}")
async def should_show(user_id: str, suggestion_type: str) -> dict[str, Any]:
    return {
        "show": _engine.should_show_suggestion(user_id, suggestion_type),
        "suggestion_type": suggestion_type,
    }
