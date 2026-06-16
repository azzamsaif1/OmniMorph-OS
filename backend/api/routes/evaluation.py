"""Evaluation API — Capability Index & Benchmarking endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.evaluation.benchmark import BenchmarkEngine
from backend.evaluation.capability_index import CapabilityIndexEngine

router = APIRouter()

_engine = CapabilityIndexEngine()
_benchmark = BenchmarkEngine()


class ObservationRequest(BaseModel):
    """Record a capability observation."""

    user_id: str = "default"
    dimension: str = Field(
        ...,
        description="One of: learning_speed, engineering_depth, execution_capability, continuous_evolution, integration_quality",
    )
    value: float = Field(..., ge=0.0, le=1.0)


class ChallengeRequest(BaseModel):
    """Request personalized challenges."""

    user_id: str = "default"
    count: int = Field(default=3, ge=1, le=10)


@router.post("/observe")
async def record_observation(req: ObservationRequest) -> dict[str, Any]:
    """Record a capability observation for a user."""
    profile = _engine.record_observation(req.user_id, req.dimension, req.value)
    return {
        "status": "recorded",
        "composite_index": round(profile.composite_index, 4),
        "dimension": req.dimension,
        "new_value": round(
            next(
                (d.value for d in profile.dimensions if d.name == req.dimension), 0.0
            ),
            4,
        ),
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: str) -> dict[str, Any]:
    """Get the full capability profile for a user."""
    return _engine.evaluate_growth(user_id)


@router.get("/benchmark/{user_id}")
async def benchmark_user(user_id: str) -> dict[str, Any]:
    """Compare user against expert baselines."""
    profile = _engine.get_or_create(user_id)
    user_scores = {d.name: d.value for d in profile.dimensions}
    results = _benchmark.compare(user_scores)
    return {
        "user_id": user_id,
        "composite_index": round(profile.composite_index, 4),
        "comparisons": [
            {
                "dimension": r.dimension,
                "user_score": r.user_score,
                "expert_p50": r.expert_p50,
                "percentile": r.percentile,
                "gap": r.gap,
            }
            for r in results
        ],
    }


@router.post("/challenges")
async def generate_challenges(req: ChallengeRequest) -> dict[str, Any]:
    """Generate personalized skill challenges."""
    profile = _engine.get_or_create(req.user_id)
    user_scores = {d.name: d.value for d in profile.dimensions}
    challenges = _benchmark.generate_challenges(user_scores, count=req.count)
    return {
        "user_id": req.user_id,
        "challenges": challenges,
    }
