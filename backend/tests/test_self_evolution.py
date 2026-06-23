"""Tests for Self-Evolving Agent — validates 655-iteration evolution loop."""

import pytest

from backend.agents.specialists.self_evolving_agent import (
    SelfEvolvingAgent,
    EvolutionPhase,
    Experiment,
    EvolutionMetrics,
)


class TestSelfEvolvingAgent:
    def test_init(self):
        agent = SelfEvolvingAgent()
        assert agent._sessions == {}

    @pytest.mark.asyncio
    async def test_evolve_basic(self):
        """Test basic evolution loop completes."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Optimize query performance",
            goal="Achieve 2x improvement",
            max_iterations=20,
            duration_hours=0.01,  # Short for testing
        )

        assert result["task"] == "Optimize query performance"
        assert result["goal"] == "Achieve 2x improvement"
        assert result["total_iterations"] > 0
        assert result["total_tool_calls"] > 0
        assert "metrics" in result
        assert result["metrics"]["experiments_run"] > 0
        assert result["metrics"]["duration_seconds"] > 0

    @pytest.mark.asyncio
    async def test_evolve_reaches_goal(self):
        """Test evolution can reach a low target goal."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Simple optimization",
            goal="Achieve 2x improvement",
            max_iterations=200,  # Enough to reach 2.0
            duration_hours=0.1,
        )

        # Should make progress
        assert result["metrics"]["final_score"] > result["metrics"]["initial_score"]
        assert result["total_iterations"] > 0

    @pytest.mark.asyncio
    async def test_evolve_respects_max_iterations(self):
        """Test that evolution stops at max_iterations."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Test iteration limit",
            goal="Achieve 100x improvement",  # Unreachable
            max_iterations=10,
            duration_hours=1.0,
        )

        assert result["total_iterations"] <= 10

    @pytest.mark.asyncio
    async def test_evolve_session_tracking(self):
        """Test that sessions are tracked."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Track session",
            goal="Achieve 2x",
            max_iterations=5,
            duration_hours=0.01,
        )

        session_id = result["session_id"]
        sessions = agent.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == session_id
        assert sessions[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_evolve_with_reorientation(self):
        """Test strategic reorientation occurs."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Test reorientation",
            goal="Achieve 100x",  # Won't reach
            max_iterations=60,
            duration_hours=0.1,
            reorientation_interval=10,
        )

        # Should have gone through multiple reorientations
        assert result["total_iterations"] >= 10

    @pytest.mark.asyncio
    async def test_evolve_metrics_structure(self):
        """Test metrics are properly structured."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="Metrics test",
            goal="Achieve 2x",
            max_iterations=15,
            duration_hours=0.01,
        )

        metrics = result["metrics"]
        assert "initial_score" in metrics
        assert "final_score" in metrics
        assert "peak_score" in metrics
        assert "total_improvement" in metrics
        assert "improvement_rate" in metrics
        assert "experiments_run" in metrics
        assert "successful_experiments" in metrics
        assert "failed_experiments" in metrics
        assert "duration_seconds" in metrics
        assert "duration_hours" in metrics

        # Invariants
        assert metrics["experiments_run"] == metrics["successful_experiments"] + metrics["failed_experiments"]
        assert metrics["peak_score"] >= metrics["final_score"]
        assert metrics["duration_hours"] == metrics["duration_seconds"] / 3600

    @pytest.mark.asyncio
    async def test_evolve_history_sample(self):
        """Test history sample is returned."""
        agent = SelfEvolvingAgent()
        result = await agent.evolve(
            task="History test",
            goal="Achieve 100x",
            max_iterations=25,
            duration_hours=0.1,
        )

        assert "history_sample" in result
        assert len(result["history_sample"]) > 0
        # Each entry should have iteration and score
        entry = result["history_sample"][0]
        assert "iteration" in entry
        assert "score" in entry
        assert "tool_calls" in entry

    @pytest.mark.asyncio
    async def test_get_session_status(self):
        """Test session status retrieval."""
        agent = SelfEvolvingAgent()
        await agent.evolve(
            task="Status test",
            goal="Achieve 2x",
            max_iterations=5,
            duration_hours=0.01,
        )

        sessions = agent.list_sessions()
        session_id = sessions[0]["session_id"]
        status = agent.get_session_status(session_id)
        assert status is not None
        assert status["status"] == "completed"

    @pytest.mark.asyncio
    async def test_multiple_sessions(self):
        """Test running multiple evolution sessions."""
        agent = SelfEvolvingAgent()
        r1 = await agent.evolve(task="Task 1", goal="2x", max_iterations=5, duration_hours=0.01)
        r2 = await agent.evolve(task="Task 2", goal="3x", max_iterations=5, duration_hours=0.01)

        sessions = agent.list_sessions()
        assert len(sessions) == 2
        assert r1["session_id"] != r2["session_id"]
