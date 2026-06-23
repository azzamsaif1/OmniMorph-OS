"""Tests for GLM-5.1 client, model registry, and inference manager."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.llm.glm_client import GLM51Client, GLMResponse, GLMSession
from backend.llm.model_registry import (
    ModelRegistry,
    ModelConfig,
    ModelFormat,
    InferenceBackend,
)
from backend.llm.inference_manager import InferenceManager, TaskType


# --- Model Registry Tests ---


class TestModelRegistry:
    def test_list_models(self):
        registry = ModelRegistry()
        models = registry.list_models()
        assert len(models) >= 3
        ids = [m["model_id"] for m in models]
        assert "glm-5.1" in ids
        assert "glm-5.1-fp8" in ids
        assert "glm-5.1-pruned" in ids

    def test_get_model(self):
        registry = ModelRegistry()
        cfg = registry.get_model("glm-5.1-fp8")
        assert cfg is not None
        assert cfg.format == ModelFormat.FP8
        assert cfg.context_window == 202752
        assert cfg.max_output_tokens == 131072
        assert cfg.parameters_b == 744.0
        assert cfg.total_experts == 256
        assert cfg.active_experts == 8
        assert cfg.license == "MIT"
        assert cfg.supports_thinking is True
        assert cfg.supports_tool_calling is True

    def test_set_active(self):
        registry = ModelRegistry()
        assert registry.active_model is None
        assert registry.set_active("glm-5.1-fp8") is True
        assert registry.active_model is not None
        assert registry.active_model.model_id == "glm-5.1-fp8"

    def test_set_active_invalid(self):
        registry = ModelRegistry()
        assert registry.set_active("nonexistent") is False

    def test_recommend_format(self):
        registry = ModelRegistry()
        # High memory → full model
        assert registry.recommend_format(141.0, 10) == "glm-5.1"
        # Medium memory → FP8
        assert registry.recommend_format(141.0, 4) == "glm-5.1-fp8"
        # Low memory → pruned
        assert registry.recommend_format(80.0, 4) == "glm-5.1-pruned"
        # Very low → FP8 remote API
        assert registry.recommend_format(16.0, 1) == "glm-5.1-fp8"

    def test_get_download_command(self):
        registry = ModelRegistry()
        cmd = registry.get_download_command("glm-5.1-fp8")
        assert cmd is not None
        assert "huggingface-cli download" in cmd
        assert "ZHIPU/GLM-5.1-FP8" in cmd

    def test_get_launch_config_vllm(self):
        registry = ModelRegistry()
        config = registry.get_launch_config("glm-5.1-fp8", InferenceBackend.VLLM)
        assert "vllm" in config["command"]
        assert "--tensor-parallel-size" in config["args"]
        assert "--enable-prefix-caching" in config["args"]

    def test_get_launch_config_sglang(self):
        registry = ModelRegistry()
        config = registry.get_launch_config("glm-5.1-fp8", InferenceBackend.SGLANG)
        assert "sglang" in config["command"]
        assert "--host" in config["args"]

    def test_check_glm_enabled_default(self):
        registry = ModelRegistry()
        # Default: disabled
        assert registry.check_glm_enabled() is False

    @patch.dict("os.environ", {"GLM51_ENABLED": "true"})
    def test_check_glm_enabled_true(self):
        registry = ModelRegistry()
        assert registry.check_glm_enabled() is True

    def test_register_custom_model(self):
        registry = ModelRegistry()
        custom = ModelConfig(
            model_id="custom-model",
            name="Custom",
            huggingface_repo="org/custom",
        )
        registry.register_model(custom)
        assert registry.get_model("custom-model") is not None


# --- GLM-5.1 Client Tests ---


class TestGLM51Client:
    def test_init_defaults(self):
        client = GLM51Client()
        assert client.model == "glm-5.1"
        assert client.thinking_mode is True
        assert client.timeout == 28800
        assert client.context_window == 202752
        assert client.max_output_tokens == 131072

    def test_enabled_default_false(self):
        client = GLM51Client()
        assert client.enabled is False

    @patch.dict("os.environ", {"GLM51_ENABLED": "true"})
    def test_enabled_when_set(self):
        client = GLM51Client()
        assert client.enabled is True

    @pytest.mark.asyncio
    async def test_generate_fallback_when_disabled(self):
        client = GLM51Client()
        response = await client.generate("Test prompt")
        assert isinstance(response, GLMResponse)
        assert "fallback" in response.finish_reason or "placeholder" in response.content.lower() or "gemini" in response.model.lower()

    @pytest.mark.asyncio
    async def test_generate_with_tools_disabled(self):
        client = GLM51Client()
        tools = [{"type": "function", "function": {"name": "test", "parameters": {}}}]
        response = await client.generate_with_tools("Test", tools)
        assert isinstance(response, GLMResponse)
        assert response.finish_reason == "fallback"

    def test_create_session(self):
        client = GLM51Client()
        session = client.create_session("test-session")
        assert isinstance(session, GLMSession)
        assert session.session_id == "test-session"
        assert session.status == "active"
        assert session.iterations == 0

    def test_get_session(self):
        client = GLM51Client()
        client.create_session("s1")
        assert client.get_session("s1") is not None
        assert client.get_session("nonexistent") is None

    def test_checkpoint_session(self):
        client = GLM51Client()
        client.create_session("s1")
        result = client.checkpoint_session("s1", {"score": 42})
        assert result is True
        session = client.get_session("s1")
        assert len(session.checkpoints) == 1
        assert session.checkpoints[0]["state"]["score"] == 42

    def test_checkpoint_nonexistent_session(self):
        client = GLM51Client()
        assert client.checkpoint_session("fake", {}) is False

    def test_end_session(self):
        client = GLM51Client()
        client.create_session("s1")
        session = client.end_session("s1")
        assert session.status == "completed"

    def test_get_stats(self):
        client = GLM51Client()
        stats = client.get_stats()
        assert stats["enabled"] is False
        assert stats["model"] == "glm-5.1"
        assert stats["context_window"] == 202752
        assert stats["total_requests"] == 0


# --- Inference Manager Tests ---


class TestInferenceManager:
    def test_init(self):
        mgr = InferenceManager()
        status = mgr.get_status()
        assert "backends" in status
        assert "vllm" in status["backends"]
        assert "sglang" in status["backends"]

    def test_select_backend_for_task(self):
        mgr = InferenceManager()
        assert mgr.select_backend_for_task("build system overnight") == TaskType.LONG_HORIZON
        assert mgr.select_backend_for_task("self-evolve and iterate") == TaskType.EVOLUTION
        assert mgr.select_backend_for_task("generate code for module") == TaskType.CODE_GENERATION
        assert mgr.select_backend_for_task("execute tool") == TaskType.TOOL_CALLING
        assert mgr.select_backend_for_task("hello world") == TaskType.REALTIME

    @pytest.mark.asyncio
    async def test_get_backend_url_default(self):
        mgr = InferenceManager()
        # Neither backend is healthy, returns preferred anyway
        url = await mgr.get_backend_url(TaskType.REALTIME)
        assert "localhost" in url

    @pytest.mark.asyncio
    async def test_check_health_no_servers(self):
        mgr = InferenceManager()
        results = await mgr.check_health()
        # No servers running, both should be unhealthy
        assert results["vllm"]["healthy"] is False
        assert results["sglang"]["healthy"] is False

    def test_record_request(self):
        mgr = InferenceManager()
        mgr.record_request(InferenceBackend.VLLM)
        status = mgr.get_status()
        assert status["backends"]["vllm"]["requests_served"] == 1

    def test_record_error(self):
        mgr = InferenceManager()
        mgr.record_error(InferenceBackend.SGLANG)
        status = mgr.get_status()
        assert status["backends"]["sglang"]["errors"] == 1

    def test_task_routing_config(self):
        mgr = InferenceManager()
        status = mgr.get_status()
        routing = status["task_routing"]
        assert routing["long_horizon"] == "vllm"
        assert routing["realtime"] == "sglang"
        assert routing["evolution"] == "vllm"
