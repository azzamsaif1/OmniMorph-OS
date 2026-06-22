"""Tests for /health and /api/system/info endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "UCSK"


@pytest.mark.anyio
async def test_system_info_structure(client):
    resp = await client.get("/api/system/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "UCSK"
    assert data["version"] == "0.1.0"

    arch = data["architecture"]
    assert len(arch["layers"]) == 6
    assert len(arch["agents"]["supervisors"]) == 5
    assert len(arch["agents"]["specialists"]) == 8
    assert len(arch["ui_modes"]) == 5

    assert len(data["features"]) >= 20
    assert "Multimodal Cognitive Sensing" in data["features"]
    assert "40+ Agent Digital Company" in data["features"]
