"""GLM-5.1 Integration API routes.

Provides endpoints for:
- GLM-5.1 status and configuration
- Self-evolving agent sessions (655+ iteration loops)
- System Genesis engine (complete system building)
- Inference backend management (vLLM/SGLang switching)
- Model registry and format recommendation

All endpoints are additive — the existing system works identically
without GLM-5.1 enabled (feature-flagged via GLM51_ENABLED env var).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from backend.llm.glm_client import GLM51Client
from backend.llm.model_registry import ModelRegistry, InferenceBackend
from backend.llm.inference_manager import InferenceManager, TaskType
from backend.agents.specialists.self_evolving_agent import SelfEvolvingAgent
from backend.core.system_genesis import SystemGenesisEngine

router = APIRouter(prefix="/api/glm", tags=["glm-5.1"])

# Module-level singletons
_glm_client = GLM51Client()
_model_registry = ModelRegistry()
_inference_manager = InferenceManager()
_evolving_agent = SelfEvolvingAgent(glm_client=_glm_client)
_genesis_engine = SystemGenesisEngine(glm_client=_glm_client)


# --- Request/Response Models ---


class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.3
    max_tokens: int = 8192
    thinking_mode: bool = True


class EvolutionRequest(BaseModel):
    task: str
    goal: str
    max_iterations: int = Field(default=655, le=1000)
    duration_hours: float = Field(default=8.0, le=24.0)
    reorientation_interval: int = Field(default=50, ge=10)


class SystemBuildRequest(BaseModel):
    specification: str
    hours: float = Field(default=8.0, le=24.0)
    max_steps: int = Field(default=1200, le=5000)
    target_size_mb: float = Field(default=5.0, le=100.0)


# --- Status & Configuration ---


@router.get("/status")
async def get_glm_status() -> dict[str, Any]:
    """Get GLM-5.1 integration status and configuration."""
    return {
        "glm51": _glm_client.get_stats(),
        "inference": _inference_manager.get_status(),
        "models": _model_registry.list_models(),
        "active_model": (
            _model_registry.active_model.model_id
            if _model_registry.active_model
            else None
        ),
        "feature_flag": _model_registry.check_glm_enabled(),
        "capabilities": {
            "thinking_mode": True,
            "tool_calling": True,
            "multi_token_prediction": True,
            "prefix_caching": True,
            "context_window": 202752,
            "max_output_tokens": 131072,
            "max_session_hours": 8,
            "max_iterations": 1000,
            "max_tool_calls": 6000,
        },
        "benchmarks": {
            "swe_bench_pro": 58.4,
            "claude_opus_4_6": 57.3,
            "gpt_5_4": 57.7,
            "autonomous_hours": 8,
            "max_iterations_demonstrated": 655,
            "max_tool_calls_demonstrated": 6000,
            "improvement_factor": 6.9,
        },
    }


@router.get("/models")
async def list_models() -> dict[str, Any]:
    """List available GLM-5.1 model variants."""
    return {
        "models": _model_registry.list_models(),
        "active": (
            _model_registry.active_model.model_id
            if _model_registry.active_model
            else None
        ),
    }


@router.post("/models/{model_id}/activate")
async def activate_model(model_id: str) -> dict[str, Any]:
    """Activate a specific model variant."""
    if not _model_registry.set_active(model_id):
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return {"activated": model_id, "config": _model_registry.get_launch_config(model_id)}


@router.get("/models/recommend")
async def recommend_model(gpu_memory_gb: float = 0, num_gpus: int = 0) -> dict[str, Any]:
    """Recommend optimal model format based on hardware resources."""
    recommended = _model_registry.recommend_format(gpu_memory_gb, num_gpus)
    return {
        "recommended": recommended,
        "download_command": _model_registry.get_download_command(recommended),
        "launch_config_vllm": _model_registry.get_launch_config(recommended, InferenceBackend.VLLM),
        "launch_config_sglang": _model_registry.get_launch_config(recommended, InferenceBackend.SGLANG),
    }


# --- Inference ---


@router.get("/inference/health")
async def inference_health() -> dict[str, Any]:
    """Check health of inference backends."""
    return await _inference_manager.check_health()


@router.get("/inference/status")
async def inference_status() -> dict[str, Any]:
    """Get full inference backend status."""
    return _inference_manager.get_status()


@router.post("/generate")
async def generate(request: GenerateRequest) -> dict[str, Any]:
    """Generate text using GLM-5.1 (falls back to Gemini if disabled)."""
    response = await _glm_client.generate(
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    return {
        "content": response.content,
        "thinking": response.thinking,
        "model": response.model,
        "finish_reason": response.finish_reason,
        "latency_ms": response.latency_ms,
        "usage": response.usage,
    }


# --- Self-Evolution ---


@router.post("/evolution/start")
async def start_evolution(request: EvolutionRequest) -> dict[str, Any]:
    """Start a self-evolution session (655+ iterations).

    The agent will iteratively improve toward the goal,
    conducting experiments, analyzing results, and applying improvements.
    Strategic reorientation occurs every N iterations.
    """
    result = await _evolving_agent.evolve(
        task=request.task,
        goal=request.goal,
        max_iterations=request.max_iterations,
        duration_hours=request.duration_hours,
        reorientation_interval=request.reorientation_interval,
    )
    return result


@router.get("/evolution/sessions")
async def list_evolution_sessions() -> dict[str, Any]:
    """List all evolution sessions."""
    return {"sessions": _evolving_agent.list_sessions()}


@router.get("/evolution/sessions/{session_id}")
async def get_evolution_session(session_id: str) -> dict[str, Any]:
    """Get status of a specific evolution session."""
    status = _evolving_agent.get_session_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    return status


# --- System Genesis ---


@router.post("/genesis/build")
async def start_system_build(request: SystemBuildRequest) -> dict[str, Any]:
    """Start building a complete system from specification.

    Inspired by GLM-5.1's ability to build Linux Desktop in 8 hours
    (1,200+ steps, 4.8MB output, equivalent to a 4-person team's week).
    """
    result = await _genesis_engine.build_system(
        specification=request.specification,
        hours=request.hours,
        max_steps=request.max_steps,
        target_size_mb=request.target_size_mb,
    )
    return result


@router.get("/genesis/sessions")
async def list_genesis_sessions() -> dict[str, Any]:
    """List all system build sessions."""
    return {"sessions": _genesis_engine.list_sessions()}


@router.get("/genesis/sessions/{session_id}")
async def get_genesis_session(session_id: str) -> dict[str, Any]:
    """Get status of a specific build session."""
    status = await _genesis_engine.get_session_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Build session not found")
    return status


# --- Comparison Data ---


@router.get("/comparison")
async def get_mythos_comparison() -> dict[str, Any]:
    """Get comparison data: GLM-5.1 vs Claude Mythos vs GPT-5.4."""
    return {
        "models": [
            {
                "name": "GLM-5.1 (OmniMorph-OS)",
                "swe_bench_pro": 58.4,
                "architecture": "MoE (256 experts, 8 active)",
                "context_window": 202752,
                "autonomous_hours": 8,
                "max_iterations": 655,
                "license": "MIT (Open Source)",
                "availability": "Open to all",
                "self_evolution": True,
                "multi_agent": True,
                "system_building": True,
            },
            {
                "name": "Claude Opus 4.6 (Mythos)",
                "swe_bench_pro": 57.3,
                "architecture": "Dense Transformer",
                "context_window": 200000,
                "autonomous_hours": 0,
                "max_iterations": 0,
                "license": "Proprietary",
                "availability": "200 organizations only",
                "self_evolution": False,
                "multi_agent": False,
                "system_building": False,
            },
            {
                "name": "GPT-5.4",
                "swe_bench_pro": 57.7,
                "architecture": "Dense Transformer",
                "context_window": 128000,
                "autonomous_hours": 0,
                "max_iterations": 0,
                "license": "Proprietary",
                "availability": "API access",
                "self_evolution": False,
                "multi_agent": False,
                "system_building": False,
            },
        ],
        "advantages": [
            "Open-source MIT license — no vendor lock-in",
            "8-hour autonomous work sessions (vs 0 for competitors)",
            "655+ iterations of self-improvement",
            "6,000+ tool calls per session",
            "Multi-agent specialized architecture",
            "Complete system building from specification",
            "6.9x performance improvements demonstrated",
            "202,752 token context window",
        ],
    }
