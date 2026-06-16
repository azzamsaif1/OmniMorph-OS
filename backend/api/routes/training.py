"""Training API — Real-World Scenario Generator (Feature 18).

Generates complete engineering projects as training scenarios based on
the user's skill level and goals. Difficulty adjusts dynamically.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class ScenarioRequest(BaseModel):
    """Request to generate a training scenario."""

    user_id: str = "default"
    domain: str = Field(
        default="backend",
        description="Target domain: backend, frontend, devops, security, distributed, ml",
    )
    difficulty: str = Field(
        default="auto",
        description="Difficulty: easy, medium, hard, expert, auto (based on capability index)",
    )
    focus_skills: list[str] = Field(
        default_factory=list,
        description="Specific skills to target in the scenario",
    )


# Pre-defined scenario templates (in production, Gemini API generates these dynamically)
_SCENARIO_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "backend": [
        {
            "title": "Build a Rate Limiter Service",
            "description": "Design and implement a distributed rate limiter using Redis with sliding window algorithm. Must handle 10K+ req/s.",
            "skills": ["distributed_systems", "redis", "algorithm_design"],
            "difficulty": "medium",
            "estimated_hours": 4,
            "milestones": [
                "Design the sliding window algorithm",
                "Implement Redis-backed storage",
                "Add cluster support with consistent hashing",
                "Write load tests proving 10K req/s throughput",
            ],
        },
        {
            "title": "Event Sourcing Microservice",
            "description": "Implement an event-sourced microservice with CQRS pattern, supporting event replay and projections.",
            "skills": ["event_sourcing", "cqrs", "postgresql", "messaging"],
            "difficulty": "hard",
            "estimated_hours": 8,
            "milestones": [
                "Define domain events and aggregates",
                "Implement event store with PostgreSQL",
                "Build read-model projections",
                "Add event replay and snapshot support",
            ],
        },
        {
            "title": "GraphQL Federation Gateway",
            "description": "Create a federated GraphQL gateway that composes schemas from 3 microservices with authentication.",
            "skills": ["graphql", "federation", "api_design", "auth"],
            "difficulty": "hard",
            "estimated_hours": 6,
            "milestones": [
                "Set up Apollo Federation gateway",
                "Create 3 subgraph services",
                "Implement cross-service entity resolution",
                "Add JWT authentication layer",
            ],
        },
    ],
    "frontend": [
        {
            "title": "Collaborative Whiteboard",
            "description": "Build a real-time collaborative whiteboard using WebSocket and Canvas API with undo/redo and multi-user cursors.",
            "skills": ["websocket", "canvas_api", "crdt", "real_time"],
            "difficulty": "hard",
            "estimated_hours": 8,
            "milestones": [
                "Implement Canvas drawing engine",
                "Add WebSocket real-time sync",
                "Implement CRDT for conflict resolution",
                "Add multi-user cursors and presence",
            ],
        },
        {
            "title": "Accessible Data Table",
            "description": "Create a fully accessible, virtualized data table component with sorting, filtering, and keyboard navigation.",
            "skills": ["accessibility", "virtualization", "react", "performance"],
            "difficulty": "medium",
            "estimated_hours": 5,
            "milestones": [
                "Implement virtual scrolling for 100K rows",
                "Add ARIA roles and keyboard navigation",
                "Implement column sorting and filtering",
                "Ensure screen reader compatibility",
            ],
        },
    ],
    "devops": [
        {
            "title": "Zero-Downtime Blue-Green Deployment",
            "description": "Set up a blue-green deployment pipeline with automated rollback, health checks, and traffic shifting.",
            "skills": ["kubernetes", "ci_cd", "nginx", "monitoring"],
            "difficulty": "hard",
            "estimated_hours": 6,
            "milestones": [
                "Configure dual environment infrastructure",
                "Implement health check probes",
                "Build automated traffic shifting",
                "Add rollback triggers on error rate threshold",
            ],
        },
    ],
    "security": [
        {
            "title": "OAuth2 Server from Scratch",
            "description": "Implement a compliant OAuth2 authorization server supporting authorization code, PKCE, and refresh token flows.",
            "skills": ["oauth2", "cryptography", "token_management", "security"],
            "difficulty": "expert",
            "estimated_hours": 10,
            "milestones": [
                "Implement authorization code flow",
                "Add PKCE extension",
                "Build refresh token rotation",
                "Implement token revocation and introspection",
            ],
        },
    ],
    "distributed": [
        {
            "title": "Raft Consensus Implementation",
            "description": "Implement the Raft consensus algorithm with leader election, log replication, and membership changes.",
            "skills": ["consensus", "distributed_systems", "networking", "fault_tolerance"],
            "difficulty": "expert",
            "estimated_hours": 12,
            "milestones": [
                "Implement leader election with randomized timeouts",
                "Build log replication with consistency guarantees",
                "Add snapshot and log compaction",
                "Handle membership changes safely",
            ],
        },
    ],
    "ml": [
        {
            "title": "Real-Time Anomaly Detector",
            "description": "Build a streaming anomaly detection service using isolation forests with auto-retraining on concept drift.",
            "skills": ["anomaly_detection", "streaming", "ml_ops", "python"],
            "difficulty": "hard",
            "estimated_hours": 7,
            "milestones": [
                "Implement isolation forest baseline",
                "Add streaming data pipeline",
                "Detect concept drift with ADWIN",
                "Trigger auto-retraining on drift",
            ],
        },
    ],
}


@router.post("/generate")
async def generate_scenario(req: ScenarioRequest) -> dict[str, Any]:
    """Generate a training scenario based on user profile and preferences."""
    domain = req.domain if req.domain in _SCENARIO_TEMPLATES else "backend"
    templates = _SCENARIO_TEMPLATES[domain]

    # Filter by difficulty if specified
    if req.difficulty != "auto":
        filtered = [t for t in templates if t["difficulty"] == req.difficulty]
        if filtered:
            templates = filtered

    # Select best matching template
    scenario = templates[0]  # In production: Gemini selects/generates dynamically

    # If focus skills specified, try to find a better match
    if req.focus_skills:
        for t in templates:
            overlap = set(t["skills"]) & set(req.focus_skills)
            if overlap:
                scenario = t
                break

    return {
        "scenario_id": uuid4().hex[:12],
        "user_id": req.user_id,
        "domain": domain,
        "title": scenario["title"],
        "description": scenario["description"],
        "skills_targeted": scenario["skills"],
        "difficulty": scenario["difficulty"],
        "estimated_hours": scenario["estimated_hours"],
        "milestones": scenario["milestones"],
        "generated_at": "dynamic",
    }


@router.get("/domains")
async def list_domains() -> dict[str, Any]:
    """List available training domains and their scenario counts."""
    return {
        "domains": {
            domain: {
                "scenario_count": len(templates),
                "difficulties": list({t["difficulty"] for t in templates}),
            }
            for domain, templates in _SCENARIO_TEMPLATES.items()
        }
    }
