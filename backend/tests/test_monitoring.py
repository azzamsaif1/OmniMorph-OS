"""Tests for the monitoring and self-healing system."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_monitoring_dashboard(client):
    resp = await client.get("/api/monitoring/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "system" in data
    assert "performance" in data
    assert "healing" in data


@pytest.mark.anyio
async def test_system_health(client):
    resp = await client.get("/api/monitoring/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_agents" in data
    assert data["total_agents"] > 0
    assert "overall_status" in data


@pytest.mark.anyio
async def test_all_agents_health(client):
    resp = await client.get("/api/monitoring/health/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert "summary" in data
    assert len(data["agents"]) > 30  # We registered 40+ agents


@pytest.mark.anyio
async def test_agent_health_specific(client):
    resp = await client.get("/api/monitoring/health/agents/recon_agent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_id"] == "recon_agent"
    assert data["domain"] == "security"
    assert "status" in data


@pytest.mark.anyio
async def test_domain_health(client):
    resp = await client.get("/api/monitoring/health/domains")
    assert resp.status_code == 200
    data = resp.json()
    assert "security" in data
    assert "finance" in data
    assert "software" in data
    assert "core" in data


@pytest.mark.anyio
async def test_performance_trends(client):
    resp = await client.get("/api/monitoring/performance/trends")
    assert resp.status_code == 200
    data = resp.json()
    assert "trends" in data
    assert "improving_count" in data
    assert "degrading_count" in data


@pytest.mark.anyio
async def test_performance_report(client):
    resp = await client.get("/api/monitoring/performance/report")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_health" in data
    assert "open_issues" in data


@pytest.mark.anyio
async def test_record_metric(client):
    resp = await client.post("/api/monitoring/metrics", json={
        "name": "test_metric",
        "value": 0.95,
        "agent": "security",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["recorded"] is True
    assert data["metric"] == "test_metric"
    assert data["value"] == 0.95


@pytest.mark.anyio
async def test_analyzer_stats(client):
    resp = await client.get("/api/monitoring/metrics/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics_tracked" in data


@pytest.mark.anyio
async def test_system_events(client):
    resp = await client.get("/api/monitoring/events")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_request_metrics(client):
    resp = await client.get("/api/monitoring/requests")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_requests" in data
    assert "window_seconds" in data


@pytest.mark.anyio
async def test_self_heal(client):
    resp = await client.post("/api/monitoring/heal")
    assert resp.status_code == 200
    data = resp.json()
    assert "diagnosis" in data
    assert "proposed_actions" in data
    assert "summary" in data


@pytest.mark.anyio
async def test_healing_history(client):
    resp = await client.get("/api/monitoring/heal/history")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_tunable_params(client):
    resp = await client.get("/api/monitoring/heal/params")
    assert resp.status_code == 200
    data = resp.json()
    assert "security.scan_timeout_ms" in data
    assert "finance.risk_tolerance" in data
    params = data["security.scan_timeout_ms"]
    assert "current" in params
    assert "min" in params
    assert "max" in params


@pytest.mark.anyio
async def test_system_resources(client):
    resp = await client.get("/api/monitoring/resources")
    assert resp.status_code == 200
    data = resp.json()
    assert "uptime_seconds" in data
    assert "cpu_count" in data


@pytest.mark.anyio
async def test_improvement_recommendations(client):
    resp = await client.get("/api/monitoring/performance/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
