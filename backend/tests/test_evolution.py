"""Tests for the self-evolving penetration testing system."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_evolution_dashboard(client):
    resp = await client.get("/api/evolution/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "overview" in data
    assert "performance_metrics" in data
    assert "memory_stats" in data
    assert "strategy_stats" in data
    assert "comparison_vs_mythos" in data


@pytest.mark.anyio
async def test_evolution_strategies(client):
    resp = await client.get("/api/evolution/strategies")
    assert resp.status_code == 200
    data = resp.json()
    assert "strategies" in data
    assert "total" in data
    assert data["total"] >= 6  # 6 base strategies
    strategies = data["strategies"]
    for s in strategies:
        assert "id" in s
        assert "name" in s
        assert "success_rate" in s
        assert "phases" in s


@pytest.mark.anyio
async def test_evolution_memory(client):
    resp = await client.get("/api/evolution/memory")
    assert resp.status_code == 200
    data = resp.json()
    assert "stats" in data
    assert "recent_experiences" in data


@pytest.mark.anyio
async def test_evolution_metrics(client):
    resp = await client.get("/api/evolution/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "current_metrics" in data
    assert "targets" in data
    metrics = data["current_metrics"]
    assert "detection_rate" in metrics
    assert "vuln_precision" in metrics
    assert "exploit_success" in metrics


@pytest.mark.anyio
async def test_record_experience(client):
    resp = await client.post("/api/evolution/experience", json={
        "target_type": "network",
        "technique": "port_scan",
        "outcome": "success",
        "tactics_used": ["tcp_connect"],
        "confidence": 0.95,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "experience_id" in data
    assert "learning_updates" in data


@pytest.mark.anyio
async def test_predict_success(client):
    resp = await client.post("/api/evolution/predict", json={
        "target_type": "network",
        "technique": "port_scan",
        "defenses": [],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "predicted_success" in data
    assert "recommendation" in data
    assert 0.0 <= data["predicted_success"] <= 1.0


@pytest.mark.anyio
async def test_evolve_strategies(client):
    resp = await client.post("/api/evolution/evolve")
    assert resp.status_code == 200
    data = resp.json()
    assert "generation" in data
    assert "mutations" in data


@pytest.mark.anyio
async def test_autonomous_assessment(client):
    resp = await client.post("/api/evolution/assess", json={
        "target_ip": "127.0.0.1",
        "depth": "quick",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "stages" in data
    assert "reconnaissance" in data["stages"]
    assert "vulnerability_analysis" in data["stages"]
    assert "exploitation" in data["stages"]
    assert "report" in data["stages"]
    assert "learning_outcomes" in data
    assert "performance_metrics" in data
