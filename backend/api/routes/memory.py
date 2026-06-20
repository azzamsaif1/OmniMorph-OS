"""Memory API — queries and manages vector / graph / event stores."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.memory.event_store import EventStore
from backend.memory.vector_store import VectorStore
from backend.memory.graph_store import GraphStore
from backend.memory.skill_diff import SkillDiffGenerator
from backend.memory.federated import FederatedNetwork
from backend.config import settings
from backend.utils.logger import log

router = APIRouter()

_event_store = EventStore(dsn=settings.postgres_dsn)
_vector_store = VectorStore(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    collection=settings.qdrant_collection,
    dim=settings.qdrant_embedding_dim,
)
_graph_store = GraphStore(uri=settings.neo4j_uri)
_skill_gen = SkillDiffGenerator()
_federated = FederatedNetwork()


class StoreEventRequest(BaseModel):
    user_id: str
    event_type: str
    description: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    user_id: str
    query_vector: list[float] = Field(default_factory=list)
    top_k: int = 5


class SkillDiffRequest(BaseModel):
    user_id: str
    skill_domain: str
    evidence: str
    difficulty: float = 0.5


class UpsertVectorRequest(BaseModel):
    vector_id: str
    vector: list[float]
    payload: dict[str, Any] = Field(default_factory=dict)


class GraphNodeRequest(BaseModel):
    label: str
    properties: dict[str, Any]


class GraphRelationRequest(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    properties: dict[str, Any] = Field(default_factory=dict)


@router.post("/events")
async def store_event(req: StoreEventRequest) -> dict[str, str]:
    """Record an event to the PostgreSQL event store."""
    try:
        await _event_store.record(
            user_id=req.user_id,
            event_type=req.event_type,
            payload=req.payload,
            description=req.description,
        )
        return {"status": "recorded", "event_type": req.event_type}
    except Exception as exc:
        log.warning("memory.event_store_error", error=str(exc))
        return {"status": "recorded_fallback", "event_type": req.event_type}


@router.get("/events/{user_id}")
async def get_events(
    user_id: str,
    event_type: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Retrieve events for a user."""
    try:
        events = await _event_store.get_events(
            user_id=user_id,
            event_type=event_type,
            limit=limit,
        )
        return {
            "user_id": user_id,
            "events": events,
            "count": len(events),
        }
    except Exception as exc:
        log.warning("memory.get_events_error", error=str(exc))
        return {"user_id": user_id, "events": [], "count": 0}


@router.post("/vectors/upsert")
async def upsert_vector(req: UpsertVectorRequest) -> dict[str, str]:
    """Insert or update a vector in Qdrant."""
    try:
        _vector_store.upsert(
            vector=req.vector,
            payload=req.payload,
            record_id=req.vector_id,
        )
        return {"status": "upserted", "vector_id": req.vector_id}
    except Exception as exc:
        log.warning("memory.vector_upsert_error", error=str(exc))
        return {"status": "upsert_fallback", "vector_id": req.vector_id}


@router.post("/search")
async def semantic_search(req: SearchRequest) -> dict[str, Any]:
    """Search the vector store for similar behavioural fingerprints."""
    try:
        if not req.query_vector:
            return {"user_id": req.user_id, "results": [], "top_k": req.top_k}
        results = _vector_store.search(
            query_vector=req.query_vector,
            top_k=req.top_k,
        )
        return {
            "user_id": req.user_id,
            "results": [
                {"id": r.id, "score": r.score, "payload": r.payload}
                for r in results
            ],
            "top_k": req.top_k,
        }
    except Exception as exc:
        log.warning("memory.search_error", error=str(exc))
        return {"user_id": req.user_id, "results": [], "top_k": req.top_k}


@router.get("/skills/{user_id}")
async def get_skill_graph(user_id: str) -> dict[str, Any]:
    """Return the user's skill graph from Neo4j."""
    try:
        skills = await _graph_store.get_user_skill_graph(user_id)
        return {"user_id": user_id, "skills": skills, "relations": []}
    except Exception as exc:
        log.warning("memory.skill_graph_error", error=str(exc))
        return {"user_id": user_id, "skills": [], "relations": []}


@router.post("/graph/node")
async def create_graph_node(req: GraphNodeRequest) -> dict[str, str]:
    """Create a node in the Neo4j graph."""
    try:
        await _graph_store.create_node(req.label, req.properties)
        return {"status": "created", "label": req.label}
    except Exception as exc:
        log.warning("memory.graph_node_error", error=str(exc))
        return {"status": "create_fallback", "label": req.label}


@router.post("/graph/relation")
async def create_graph_relation(req: GraphRelationRequest) -> dict[str, str]:
    """Create a relationship in the Neo4j graph."""
    try:
        await _graph_store.create_relation(
            req.source_id, req.target_id, req.relation_type
        )
        return {"status": "created", "type": req.relation_type}
    except Exception as exc:
        log.warning("memory.graph_relation_error", error=str(exc))
        return {"status": "create_fallback", "type": req.relation_type}


@router.post("/skill-diff/generate")
async def generate_skill_diff(req: SkillDiffRequest) -> dict[str, Any]:
    """Generate a Skill Diff from user evidence via Gemini."""
    diff = await _skill_gen.generate(
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
    return _federated.stats()


@router.post("/federated/offer")
async def offer_skill_diff(
    diff_id: str = "",
    skill_domain: str = "",
) -> dict[str, str]:
    """Offer a skill diff to the federated network."""
    from backend.memory.skill_diff import SkillDiff

    diff = SkillDiff(
        diff_id=diff_id,
        source_anon_id="anonymous",
        skill_domain=skill_domain,
        abstraction="",
        exercises=[],
        difficulty=0.5,
        metadata={},
    )
    _federated.offer_skill_diff(diff)
    return {"status": "offered", "diff_id": diff_id}


@router.get("/federated/search")
async def search_federated_diffs(skill_domain: str = "") -> dict[str, Any]:
    """Search available skill diffs in the network."""
    diffs = _federated.search_diffs(skill_domain)
    return {
        "results": [
            {
                "diff_id": d.diff_id,
                "skill_domain": d.skill_domain,
                "difficulty": d.difficulty,
                "abstraction": d.abstraction,
            }
            for d in diffs
        ],
        "count": len(diffs),
    }
