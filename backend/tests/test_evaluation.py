"""Tests for evaluation API — capability index, benchmarks, challenges."""

from __future__ import annotations

import pytest

from backend.evaluation.capability_index import (
    CapabilityIndexEngine,
    CapabilityProfile,
    DimensionScore,
)


class TestDimensionScore:
    def test_default_value(self):
        d = DimensionScore(name="learning_speed")
        assert d.value == 0.0
        assert d.samples == 0

    def test_update_ema(self):
        d = DimensionScore(name="test")
        d.update(1.0, alpha=0.1)
        assert abs(d.value - 0.1) < 1e-6
        assert d.samples == 1

    def test_multiple_updates_converge(self):
        d = DimensionScore(name="test")
        for _ in range(100):
            d.update(0.8)
        assert abs(d.value - 0.8) < 0.05


class TestCapabilityProfile:
    def test_five_dimensions(self):
        p = CapabilityProfile(user_id="test")
        assert len(p.dimensions) == 5

    def test_dimension_names(self):
        p = CapabilityProfile(user_id="test")
        names = [d.name for d in p.dimensions]
        assert "learning_speed" in names
        assert "engineering_depth" in names
        assert "execution_capability" in names
        assert "continuous_evolution" in names
        assert "integration_quality" in names

    def test_initial_composite_zero(self):
        p = CapabilityProfile(user_id="test")
        assert p.composite_index == 0.0

    def test_to_dict(self):
        p = CapabilityProfile(user_id="test")
        d = p.to_dict()
        assert d["user_id"] == "test"
        assert "composite_index" in d
        assert "dimensions" in d


class TestCapabilityEngine:
    def test_get_or_create(self):
        engine = CapabilityIndexEngine()
        p = engine.get_or_create("u1")
        assert p.user_id == "u1"

    def test_record_observation(self):
        engine = CapabilityIndexEngine()
        p = engine.record_observation("u1", "learning_speed", 0.9)
        assert p.learning_speed.value > 0

    def test_evaluate_growth(self):
        engine = CapabilityIndexEngine()
        engine.record_observation("u1", "engineering_depth", 0.7)
        result = engine.evaluate_growth("u1")
        assert result["user_id"] == "u1"
        assert "maturity_level" in result
        assert "dimensions" in result


@pytest.mark.anyio
async def test_observe_api(client):
    resp = await client.post(
        "/api/evaluation/observe",
        json={"user_id": "test-u", "dimension": "learning_speed", "value": 0.75},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "recorded"
    assert data["dimension"] == "learning_speed"
    assert data["new_value"] > 0


@pytest.mark.anyio
async def test_profile_api(client):
    resp = await client.get("/api/evaluation/profile/test-u")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "test-u"
    assert "composite_index" in data
    assert "maturity_level" in data
    assert "dimensions" in data


@pytest.mark.anyio
async def test_benchmark_api(client):
    resp = await client.get("/api/evaluation/benchmark/test-u")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "test-u"
    assert "composite_index" in data
    assert "comparisons" in data


@pytest.mark.anyio
async def test_challenges_api(client):
    resp = await client.post(
        "/api/evaluation/challenges",
        json={"user_id": "test-u", "count": 3},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "test-u"
    assert "challenges" in data
