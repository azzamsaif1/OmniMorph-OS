"""Model Registry — configuration and format selection for LLM models.

Manages available model configurations, hardware detection, and dynamic
format selection (FP8 vs BF16) based on available resources.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelFormat(str, Enum):
    FP8 = "fp8"
    BF16 = "bf16"
    FULL = "full"
    PRUNED = "pruned"


class InferenceBackend(str, Enum):
    VLLM = "vllm"
    SGLANG = "sglang"
    API = "api"  # Remote API endpoint


@dataclass
class ModelConfig:
    """Configuration for a registered model."""

    model_id: str
    name: str
    huggingface_repo: str
    format: ModelFormat = ModelFormat.FP8
    context_window: int = 202752
    max_output_tokens: int = 131072
    parameters_b: float = 744.0
    active_experts: int = 8
    total_experts: int = 256
    training_tokens_t: float = 28.5
    license: str = "MIT"
    supports_thinking: bool = True
    supports_tool_calling: bool = True
    supports_mtp: bool = True
    min_gpus: int = 8
    gpu_memory_gb: float = 141.0
    storage_gb: float = 400.0
    metadata: dict[str, Any] = field(default_factory=dict)


# Pre-configured GLM-5.1 variants
GLM_51_CONFIGS = {
    "glm-5.1": ModelConfig(
        model_id="glm-5.1",
        name="GLM-5.1 (Full)",
        huggingface_repo="zai-org/GLM-5.1",
        format=ModelFormat.FULL,
        storage_gb=1400.0,
    ),
    "glm-5.1-fp8": ModelConfig(
        model_id="glm-5.1-fp8",
        name="GLM-5.1 (FP8 Compressed)",
        huggingface_repo="ZHIPU/GLM-5.1-FP8",
        format=ModelFormat.FP8,
        storage_gb=400.0,
    ),
    "glm-5.1-pruned": ModelConfig(
        model_id="glm-5.1-pruned",
        name="GLM-5.1 (Pruned 60%)",
        huggingface_repo="zai-org/GLM-5.1-Pruned",
        format=ModelFormat.PRUNED,
        parameters_b=450.0,
        storage_gb=250.0,
        min_gpus=4,
    ),
}


class ModelRegistry:
    """Central registry for all available LLM models.

    Manages model configurations, checks hardware compatibility,
    and recommends optimal format based on available resources.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelConfig] = dict(GLM_51_CONFIGS)
        self._active_model: str | None = None

    @property
    def active_model(self) -> ModelConfig | None:
        if self._active_model:
            return self._models.get(self._active_model)
        return None

    def register_model(self, config: ModelConfig) -> None:
        self._models[config.model_id] = config

    def get_model(self, model_id: str) -> ModelConfig | None:
        return self._models.get(model_id)

    def list_models(self) -> list[dict[str, Any]]:
        return [
            {
                "model_id": cfg.model_id,
                "name": cfg.name,
                "format": cfg.format.value,
                "parameters_b": cfg.parameters_b,
                "context_window": cfg.context_window,
                "storage_gb": cfg.storage_gb,
                "license": cfg.license,
                "supports_thinking": cfg.supports_thinking,
                "supports_tool_calling": cfg.supports_tool_calling,
            }
            for cfg in self._models.values()
        ]

    def set_active(self, model_id: str) -> bool:
        if model_id in self._models:
            self._active_model = model_id
            return True
        return False

    def recommend_format(self, available_gpu_memory_gb: float = 0, num_gpus: int = 0) -> str:
        """Recommend optimal model format based on hardware resources."""
        total_memory = available_gpu_memory_gb * num_gpus

        if total_memory >= 1400:
            return "glm-5.1"
        elif total_memory >= 400:
            return "glm-5.1-fp8"
        elif total_memory >= 250:
            return "glm-5.1-pruned"
        else:
            # Fallback: use remote API
            return "glm-5.1-fp8"

    def get_download_command(self, model_id: str) -> str | None:
        cfg = self._models.get(model_id)
        if not cfg:
            return None
        local_dir = f"./models/{model_id}"
        return f"huggingface-cli download {cfg.huggingface_repo} --local-dir {local_dir}"

    def get_launch_config(self, model_id: str, backend: InferenceBackend = InferenceBackend.VLLM) -> dict[str, Any]:
        """Get launch configuration for the specified backend."""
        cfg = self._models.get(model_id)
        if not cfg:
            return {}

        if backend == InferenceBackend.VLLM:
            return {
                "command": "python -m vllm.entrypoints.openai.api_server",
                "args": {
                    "--model": f"./models/{model_id}",
                    "--tensor-parallel-size": str(cfg.min_gpus),
                    "--max-model-len": str(min(cfg.context_window, 200000)),
                    "--port": "8100",
                    "--enable-prefix-caching": "",
                },
                "env": {
                    "CUDA_VISIBLE_DEVICES": ",".join(str(i) for i in range(cfg.min_gpus)),
                },
            }
        elif backend == InferenceBackend.SGLANG:
            return {
                "command": "python3 -m sglang.launch_server",
                "args": {
                    "--model-path": f"./models/{model_id}",
                    "--host": "0.0.0.0",
                    "--port": "30000",
                },
                "env": {},
            }
        return {}

    def check_glm_enabled(self) -> bool:
        """Check if GLM-5.1 is enabled via feature flag."""
        return os.environ.get("GLM51_ENABLED", "false").lower() in ("true", "1", "yes")

    def get_glm_endpoint(self) -> str:
        """Get the GLM-5.1 inference endpoint URL."""
        return os.environ.get("GLM51_ENDPOINT", "http://localhost:8100/v1")
