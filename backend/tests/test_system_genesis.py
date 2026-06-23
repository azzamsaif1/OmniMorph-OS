"""Tests for System Genesis Engine — validates complete system building."""

import pytest

from backend.core.system_genesis import (
    SystemGenesisEngine,
    BuildPhase,
    BuildStep,
    SystemComponent,
    BuildSession,
)


class TestSystemGenesisEngine:
    def test_init(self):
        engine = SystemGenesisEngine()
        assert engine._sessions == {}

    @pytest.mark.asyncio
    async def test_build_linux_desktop(self):
        """Test building a Linux Desktop system (inspired by GLM-5.1 demo)."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Linux desktop environment with window manager, "
                         "status bar, VPN manager, and Chinese font support",
            hours=0.01,  # Short for testing
            max_steps=100,
        )

        assert result["status"] == "completed"
        assert result["specification"].startswith("Linux desktop")

        # Architecture should detect desktop components
        arch = result["architecture"]
        assert arch["system_type"] == "desktop_application"
        comp_names = [c["name"] for c in arch["components"]]
        assert "window_manager" in comp_names
        assert "status_bar" in comp_names
        assert "vpn_manager" in comp_names
        assert "font_manager" in comp_names

        # Metrics
        metrics = result["metrics"]
        assert metrics["total_steps"] > 0
        assert metrics["completed_steps"] > 0
        assert metrics["components_built"] > 0
        assert metrics["files_created"] > 0
        assert metrics["test_coverage"] > 0

    @pytest.mark.asyncio
    async def test_build_web_app(self):
        """Test building a web application."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Web API with authentication and frontend",
            hours=0.01,
            max_steps=50,
        )

        assert result["status"] == "completed"
        arch = result["architecture"]
        assert arch["system_type"] == "web_application"
        comp_names = [c["name"] for c in arch["components"]]
        assert "api_server" in comp_names
        assert "auth_module" in comp_names

    @pytest.mark.asyncio
    async def test_build_cli_tool(self):
        """Test building a CLI tool."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Command-line tool for data processing",
            hours=0.01,
            max_steps=30,
        )

        assert result["status"] == "completed"
        arch = result["architecture"]
        assert arch["system_type"] == "cli_tool"

    @pytest.mark.asyncio
    async def test_build_metrics_complete(self):
        """Test that all metrics are populated."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Simple library with tests",
            hours=0.01,
            max_steps=50,
        )

        metrics = result["metrics"]
        assert "total_steps" in metrics
        assert "completed_steps" in metrics
        assert "failed_steps" in metrics
        assert "files_created" in metrics
        assert "total_size_mb" in metrics
        assert "duration_seconds" in metrics
        assert "duration_hours" in metrics
        assert "components_built" in metrics
        assert "test_coverage" in metrics
        assert "lines_of_code" in metrics

        assert metrics["failed_steps"] == 0
        assert metrics["duration_hours"] == metrics["duration_seconds"] / 3600

    @pytest.mark.asyncio
    async def test_build_deployment_ready(self):
        """Test deployment readiness check."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Production web service",
            hours=0.01,
            max_steps=50,
        )

        # Should be deployment ready (coverage > 60%, no failures)
        assert result["deployment_ready"] is True

    @pytest.mark.asyncio
    async def test_session_tracking(self):
        """Test that build sessions are tracked."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Test project",
            hours=0.01,
            max_steps=20,
        )

        sessions = engine.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["status"] == "completed"
        assert sessions[0]["session_id"] == result["session_id"]

    @pytest.mark.asyncio
    async def test_get_session_status(self):
        """Test session status retrieval."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Status test project",
            hours=0.01,
            max_steps=20,
        )

        status = await engine.get_session_status(result["session_id"])
        assert status is not None
        assert status["status"] == "completed"
        assert status["phase"] == "completed"

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self):
        """Test getting a nonexistent session returns None."""
        engine = SystemGenesisEngine()
        status = await engine.get_session_status("nonexistent")
        assert status is None

    @pytest.mark.asyncio
    async def test_multiple_builds(self):
        """Test running multiple builds."""
        engine = SystemGenesisEngine()

        r1 = await engine.build_system("Project A", hours=0.01, max_steps=10)
        r2 = await engine.build_system("Project B", hours=0.01, max_steps=10)

        sessions = engine.list_sessions()
        assert len(sessions) == 2
        assert r1["session_id"] != r2["session_id"]

    @pytest.mark.asyncio
    async def test_components_have_coverage(self):
        """Test that components have test coverage after build."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Desktop with window manager",
            hours=0.01,
            max_steps=50,
        )

        for comp in result["components"]:
            assert comp["status"] in ("built", "tested")
            assert comp["test_coverage"] > 0

    @pytest.mark.asyncio
    async def test_assembly_validation(self):
        """Test final assembly produces validation results."""
        engine = SystemGenesisEngine()

        result = await engine.build_system(
            specification="Validated system",
            hours=0.01,
            max_steps=30,
        )

        assert "assembly" in result
        assert result["assembly"]["assembled"] is True
        assert result["assembly"]["validation"]["all_components_built"] is True
        assert result["assembly"]["validation"]["integration_verified"] is True
