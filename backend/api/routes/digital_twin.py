"""Digital Twin API — portable engineering mind clone (Feature 11)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agents.specialists.digital_twin import DigitalTwinEngine
from backend.agents.specialists.competitive_twin import CompetitiveTwinEngine

router = APIRouter()

_twin_engine = DigitalTwinEngine()
_competitive = CompetitiveTwinEngine()


class CaptureRequest(BaseModel):
    user_id: str = "default"
    language: str = ""
    framework: str = ""
    pattern_type: str = ""
    pattern_desc: str = ""
    context: str = ""


class CompeteChallengeRequest(BaseModel):
    user_id: str = "default"
    domain: str = "backend"
    difficulty: str = "auto"


class CompeteSubmitRequest(BaseModel):
    user_id: str = "default"
    challenge_id: str
    user_score: float
    user_time: float
    domain: str = "backend"
    difficulty: str = "medium"


@router.post("/capture")
async def capture_activity(req: CaptureRequest) -> dict[str, Any]:
    fp = _twin_engine.capture_activity(
        user_id=req.user_id,
        language=req.language,
        framework=req.framework,
        pattern_type=req.pattern_type,
        pattern_desc=req.pattern_desc,
        context=req.context,
    )
    return fp.to_dict()


@router.get("/fingerprint/{user_id}")
async def get_fingerprint(user_id: str) -> dict[str, Any]:
    fp = _twin_engine.get_or_create(user_id)
    return fp.to_dict()


@router.get("/predict/{user_id}")
async def predict_behavior(user_id: str) -> dict[str, Any]:
    return _twin_engine.predict_behavior(user_id, {})


@router.post("/export/{user_id}")
async def export_soul(user_id: str) -> dict[str, Any]:
    soul = _twin_engine.export_soul(user_id)
    return soul.to_dict()


@router.post("/import")
async def import_soul(body: dict[str, Any]) -> dict[str, Any]:
    import json
    soul_json = json.dumps(body)
    user_id = _twin_engine.import_soul(soul_json)
    return {"status": "imported", "user_id": user_id}


@router.get("/compare/{user_a}/{user_b}")
async def compare_twins(user_a: str, user_b: str) -> dict[str, Any]:
    return _twin_engine.compare_twins(user_a, user_b)


# --- Competitive Twin endpoints ---


@router.post("/compete/challenge")
async def generate_challenge(req: CompeteChallengeRequest) -> dict[str, Any]:
    return await _competitive.generate_challenge(
        user_id=req.user_id,
        domain=req.domain,
        difficulty=req.difficulty,
    )


@router.post("/compete/submit")
async def submit_challenge(req: CompeteSubmitRequest) -> dict[str, Any]:
    result = await _competitive.submit_result(
        user_id=req.user_id,
        challenge_id=req.challenge_id,
        user_score=req.user_score,
        user_time=req.user_time,
        domain=req.domain,
        difficulty=req.difficulty,
    )
    return {
        "challenge_id": result.challenge_id,
        "winner": result.winner,
        "user_score": result.user_score,
        "twin_score": round(result.twin_score, 3),
        "user_time_sec": result.user_time_sec,
        "twin_time_sec": round(result.twin_time_sec, 1),
        "feedback": result.feedback,
    }


@router.get("/compete/stats/{user_id}")
async def get_compete_stats(user_id: str) -> dict[str, Any]:
    return _competitive.get_stats(user_id)
