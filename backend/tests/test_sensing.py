"""Tests for sensing API — behavior recording and mental state."""

from __future__ import annotations

import pytest

from backend.sensing.behavior_analyzer import BehaviorAnalyzer, BehaviorMetrics
from backend.sensing.mental_state import CognitiveState, MentalStateFuser


class TestBehaviorAnalyzer:
    def test_empty_metrics(self):
        ba = BehaviorAnalyzer()
        m = ba.compute_metrics()
        assert m.typing_speed_cpm == 0.0
        assert m.error_rate == 0.0
        assert m.activity_score == 0.0

    def test_record_keystroke(self):
        ba = BehaviorAnalyzer()
        for _ in range(10):
            ba.record_keystroke("a")
        m = ba.compute_metrics()
        assert m.typing_speed_cpm > 0

    def test_error_rate_from_backspaces(self):
        ba = BehaviorAnalyzer()
        for _ in range(8):
            ba.record_keystroke("a")
        for _ in range(2):
            ba.record_keystroke("backspace")
        m = ba.compute_metrics()
        assert abs(m.error_rate - 0.2) < 0.01

    def test_mouse_velocity(self):
        ba = BehaviorAnalyzer()
        ba.record_mouse_move(0, 0)
        import time
        time.sleep(0.01)
        ba.record_mouse_move(100, 100)
        m = ba.compute_metrics()
        assert m.mouse_velocity > 0

    def test_reset_clears_data(self):
        ba = BehaviorAnalyzer()
        ba.record_keystroke("x")
        ba.record_click()
        ba.reset()
        m = ba.compute_metrics()
        assert m.typing_speed_cpm == 0.0


class TestMentalStateFuser:
    def test_idle_state_with_no_input(self):
        fuser = MentalStateFuser()
        ms = fuser.fuse()
        assert ms.state in CognitiveState
        assert 0 <= ms.confidence <= 1
        assert 0 <= ms.focus_score <= 1

    def test_behavior_only_fusion(self):
        fuser = MentalStateFuser()
        metrics = BehaviorMetrics(
            typing_speed_cpm=200,
            error_rate=0.05,
            idle_gap_sec=2.0,
            activity_score=0.8,
        )
        ms = fuser.fuse(behavior=metrics)
        assert ms.focus_score > 0.3

    def test_raw_vector_length(self):
        fuser = MentalStateFuser()
        ms = fuser.fuse()
        assert len(ms.raw_vector) == 4

    def test_all_scores_bounded(self):
        fuser = MentalStateFuser()
        ms = fuser.fuse()
        assert 0 <= ms.focus_score <= 1
        assert 0 <= ms.fatigue_score <= 1
        assert 0 <= ms.frustration_score <= 1
        assert 0 <= ms.engagement_score <= 1


@pytest.mark.anyio
async def test_record_behavior_api(client):
    resp = await client.post(
        "/api/sensing/behavior",
        json={"event_type": "keystroke", "key": "a"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"


@pytest.mark.anyio
async def test_record_mouse_move_api(client):
    resp = await client.post(
        "/api/sensing/behavior",
        json={"event_type": "mouse_move", "x": 100.0, "y": 200.0},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"


@pytest.mark.anyio
async def test_get_current_state_api(client):
    resp = await client.get("/api/sensing/state")
    assert resp.status_code == 200
    data = resp.json()
    assert "state" in data
    assert "confidence" in data
    assert "focus_score" in data
    assert "fatigue_score" in data
    assert "frustration_score" in data
    assert "engagement_score" in data
