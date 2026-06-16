"""Memory API — queries and manages vector / graph / event stores."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class StoreEventRequest(BaseModel):
    user_id: str
    event_type: str
    description: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = 5


class SkillDiffRequest(BaseModel):
    user_id: str
    skill_domain: str
    evidence: str
    difficulty: float = 0.5


@router.post("/events")
async def store_event(req: StoreEventRequest) -> dict[str, str]:
    """Record an event to the PostgreSQL event store."""
    # In production, this calls EventStore.record()
    return {"status": "recorded", "event_type": req.event_type}


@router.get("/events/{user_id}")
async def get_events(
    user_id: str,
    event_type: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Retrieve events for a user."""
    return {"user_id": user_id, "events": [], "count": 0}


@router.post("/search")
async def semantic_search(req: SearchRequest) -> dict[str, Any]:
    """Search the vector store for similar behavioural fingerprints."""
    return {"user_id": req.user_id, "results": [], "top_k": req.top_k}


@router.get("/skills/{user_id}")
async def get_skill_graph(user_id: str) -> dict[str, Any]:
    """Return the user's skill graph from Neo4j."""
    return {"user_id": user_id, "skills": [], "relations": []}


@router.post("/skill-diff/generate")
async def generate_skill_diff(req: SkillDiffRequest) -> dict[str, Any]:
    """Generate a Skill Diff from user evidence via Gemini."""
    from backend.memory.skill_diff import SkillDiffGenerator

    generator = SkillDiffGenerator()
    diff = await generator.generate(
        user_id=req.user_id,
        skill_domain=req.skill_domain,
        evidence=req.evidence,
        difficulty=req.difficulty,
    )
    return {
        "diff_id": diff.diff_id,
        "skill_domain": diff.skill_domain,
        "abstraction": diff.abstraction,
        "exercises": diff.exercises,
        "difficulty": diff.difficulty,
    }


@router.get("/federated/stats")
async def federated_stats() -> dict[str, Any]:
    """Return P2P network statistics."""
    from backend.memory.federated import FederatedNetwork

    net = FederatedNetwork()
    return net.stats()
