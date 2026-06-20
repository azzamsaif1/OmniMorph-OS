"""Enterprise API — team dashboard & organisational analytics (Feature 20)."""

from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.evaluation.capability_index import CapabilityIndexEngine
from backend.gemini_client import gemini_career_advice, gemini_generate_scenario
from backend.utils.logger import log

router = APIRouter()

_capability = CapabilityIndexEngine()

# In-memory team store for MVP
_teams: dict[str, dict[str, Any]] = {
    "team-alpha": {
        "team_id": "team-alpha",
        "name": "Alpha Team",
        "members": [
            {"user_id": "u1", "display_name": "eng_a7f3", "role": "senior"},
            {"user_id": "u2", "display_name": "eng_b2e1", "role": "mid"},
            {"user_id": "u3", "display_name": "eng_c9d4", "role": "junior"},
            {"user_id": "u4", "display_name": "eng_d1f8", "role": "mid"},
            {"user_id": "u5", "display_name": "eng_e5a2", "role": "senior"},
        ],
    }
}


class TeamMember(BaseModel):
    user_id: str
    display_name: str
    role: str = "developer"


class TeamMetrics(BaseModel):
    team_id: str
    name: str = ""
    total_members: int
    avg_focus_score: float
    avg_productivity: float
    cognitive_diversity: float
    top_skills: list[str]
    metrics: dict[str, float] = Field(default_factory=dict)


@router.get("/dashboard/{team_id}", response_model=TeamMetrics)
async def get_dashboard(team_id: str) -> dict[str, Any]:
    """Return aggregated team cognitive metrics (privacy-safe)."""
    team = _teams.get(team_id, {})
    members = team.get("members", [])

    total = len(members)
    focus_scores = []
    prod_scores = []
    for m in members:
        profile = _capability.get_or_create(m["user_id"])
        focus_scores.append(profile.execution_capability.value)
        prod_scores.append(profile.composite_index)

    avg_focus = sum(focus_scores) / max(total, 1)
    avg_prod = sum(prod_scores) / max(total, 1)

    unique_strengths = set()
    for m in members:
        profile = _capability.get_or_create(m["user_id"])
        for d in profile.dimensions:
            if d.value > 0.6:
                unique_strengths.add(d.name)

    diversity = len(unique_strengths) / 5.0

    return TeamMetrics(
        team_id=team_id,
        name=team.get("name", team_id),
        total_members=total,
        avg_focus_score=round(avg_focus, 3),
        avg_productivity=round(avg_prod, 3),
        cognitive_diversity=round(diversity, 3),
        top_skills=sorted(unique_strengths),
        metrics={
            "productivity": round(avg_prod * 100, 1),
            "creativity": round(diversity * 80, 1),
            "cohesion": 82.0,
            "focus_index": round(avg_focus * 100, 1),
        },
    ).model_dump()


@router.get("/leaderboard/{team_id}")
async def leaderboard(team_id: str, limit: int = 10) -> dict[str, Any]:
    """Anonymous leaderboard based on skill progression (Feature 12)."""
    team = _teams.get(team_id, {})
    members = team.get("members", [])

    entries = []
    for m in members:
        profile = _capability.get_or_create(m["user_id"])
        entries.append({
            "anonymous_id": m.get("display_name", m["user_id"][:8]),
            "capability_index": round(profile.composite_index * 100, 1),
            "growth": round(profile.continuous_evolution.value * 30, 1),
            "top_dimension": max(
                profile.dimensions, key=lambda d: d.value
            ).name if profile.dimensions else "",
        })

    entries.sort(key=lambda e: e["capability_index"], reverse=True)
    return {"team_id": team_id, "entries": entries[:limit], "limit": limit}


@router.post("/team/{team_id}/members")
async def add_member(team_id: str, member: TeamMember) -> dict[str, str]:
    if team_id not in _teams:
        _teams[team_id] = {"team_id": team_id, "name": team_id, "members": []}
    _teams[team_id]["members"].append({
        "user_id": member.user_id,
        "display_name": member.display_name,
        "role": member.role,
    })
    log.info("enterprise.member_added", team=team_id, user=member.user_id)
    return {"status": "added", "team_id": team_id, "user_id": member.user_id}


@router.get("/career/{user_id}")
async def career_simulation(user_id: str) -> dict[str, Any]:
    """Career & Professional Evolution Simulator (Feature 19)."""
    profile = _capability.get_or_create(user_id)
    cap_dict = {d.name: round(d.value, 3) for d in profile.dimensions}

    advice = await gemini_career_advice(
        capability_profile=cap_dict,
        current_role="developer",
    )

    return {
        "user_id": user_id,
        "current_level": advice.get("current_assessment", "mid"),
        "strongest_domain": max(cap_dict, key=cap_dict.get) if cap_dict else "Backend Systems",
        "growth_velocity": f"+{round(profile.continuous_evolution.value * 20, 1)}%/quarter",
        "predicted_path": advice.get("paths", []),
        "paths": advice.get("paths", []),
        "recommendations": advice.get("immediate_actions", []),
    }


@router.post("/scenario/generate")
async def generate_scenario(
    skill_level: str = "intermediate",
    domain: str = "backend",
) -> dict[str, Any]:
    """Real-world Scenario Generator (Feature 18)."""
    result = await gemini_generate_scenario(
        domain=domain,
        difficulty="medium" if skill_level == "intermediate" else skill_level,
        skills=[domain, "problem_solving", "testing"],
        user_level=skill_level,
    )
    return {
        "skill_level": skill_level,
        "domain": domain,
        "scenario": result.get("title", "Dynamic Scenario"),
        "description": result.get("description", ""),
        "objectives": result.get("milestones", []),
        "difficulty": result.get("difficulty", 0.5),
    }


@router.get("/teams")
async def list_teams() -> dict[str, Any]:
    """List all teams."""
    return {
        "teams": [
            {
                "team_id": t["team_id"],
                "name": t.get("name", t["team_id"]),
                "member_count": len(t.get("members", [])),
            }
            for t in _teams.values()
        ]
    }
