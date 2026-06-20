"""Tests for enterprise API — team dashboard, leaderboard, career, scenarios."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_team_dashboard(client):
    resp = await client.get("/api/enterprise/dashboard/team-alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["team_id"] == "team-alpha"
    assert data["name"] == "Alpha Team"
    assert data["total_members"] == 5
    assert "avg_focus_score" in data
    assert "avg_productivity" in data
    assert "cognitive_diversity" in data
    assert "metrics" in data
    metrics = data["metrics"]
    assert "productivity" in metrics
    assert "creativity" in metrics
    assert "cohesion" in metrics
    assert "focus_index" in metrics


@pytest.mark.anyio
async def test_team_dashboard_unknown_team(client):
    resp = await client.get("/api/enterprise/dashboard/nonexistent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_members"] == 0


@pytest.mark.anyio
async def test_leaderboard(client):
    resp = await client.get("/api/enterprise/leaderboard/team-alpha")
    assert resp.status_code == 200
    data = resp.json()
    assert data["team_id"] == "team-alpha"
    assert len(data["entries"]) == 5
    entry = data["entries"][0]
    assert "anonymous_id" in entry
    assert "capability_index" in entry
    assert "growth" in entry
    assert "top_dimension" in entry


@pytest.mark.anyio
async def test_leaderboard_sorted_descending(client):
    resp = await client.get("/api/enterprise/leaderboard/team-alpha")
    entries = resp.json()["entries"]
    indices = [e["capability_index"] for e in entries]
    assert indices == sorted(indices, reverse=True)


@pytest.mark.anyio
async def test_add_member(client):
    resp = await client.post(
        "/api/enterprise/team/test-team/members",
        json={"user_id": "new-user", "display_name": "Test User", "role": "junior"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "added"
    assert data["team_id"] == "test-team"


@pytest.mark.anyio
async def test_list_teams(client):
    resp = await client.get("/api/enterprise/teams")
    assert resp.status_code == 200
    data = resp.json()
    assert "teams" in data
    team_ids = [t["team_id"] for t in data["teams"]]
    assert "team-alpha" in team_ids


@pytest.mark.anyio
async def test_career_simulation(client):
    resp = await client.get("/api/enterprise/career/u1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "u1"
    assert "current_level" in data
    assert "strongest_domain" in data
    assert "growth_velocity" in data
    assert "recommendations" in data


@pytest.mark.anyio
async def test_generate_scenario(client):
    resp = await client.post(
        "/api/enterprise/scenario/generate",
        params={"skill_level": "intermediate", "domain": "backend"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["skill_level"] == "intermediate"
    assert data["domain"] == "backend"
    assert "scenario" in data
    assert "objectives" in data
