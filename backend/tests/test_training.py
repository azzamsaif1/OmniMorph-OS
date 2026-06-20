"""Tests for training / scenario generation (via enterprise endpoint)."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_scenario_generation_default_params(client):
    resp = await client.post("/api/enterprise/scenario/generate")
    assert resp.status_code == 200
    data = resp.json()
    assert "scenario" in data
    assert "domain" in data
    assert "objectives" in data
    assert "difficulty" in data


@pytest.mark.anyio
async def test_scenario_generation_custom_params(client):
    resp = await client.post(
        "/api/enterprise/scenario/generate",
        params={"skill_level": "advanced", "domain": "security"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["skill_level"] == "advanced"
    assert data["domain"] == "security"


@pytest.mark.anyio
async def test_scenario_has_title(client):
    resp = await client.post("/api/enterprise/scenario/generate")
    data = resp.json()
    assert isinstance(data["scenario"], str)
    assert len(data["scenario"]) > 0
