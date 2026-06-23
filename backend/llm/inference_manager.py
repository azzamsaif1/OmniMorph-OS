"""Inference Manager — dynamic engine switching between vLLM and SGLang.

Automatically selects the optimal inference backend based on task type:
- vLLM: Heavy long-horizon tasks (code generation, system building)
- SGLang: Real-time interactions (chat, quick completions)

Manages health checks, failover, and load balancing.
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx

from backend.llm.model_registry import InferenceBackend
from backend.utils.logger import log


class TaskType(str, Enum):
    LONG_HORIZON = "long_horizon"  # 8-hour tasks, system building
    REALTIME = "realtime"  # Chat, quick responses
    TOOL_CALLING = "tool_calling"  # Multi-step tool execution
    EVOLUTION = "evolution"  # Self-evolution iterations
    CODE_GENERATION = "code_generation"  # Large code outputs


@dataclass
class BackendStatus:
    """Health status of an inference backend."""

    backend: InferenceBackend
    url: str
    healthy: bool = False
    last_check: float = 0.0
    latency_ms: float = 0.0
    requests_served: int = 0
    errors: int = 0
    gpu_utilization: float = 0.0


class InferenceManager:
    """Manages inference backends for GLM-5.1 with automatic switching.

    Routes requests to the optimal backend based on task type:
    - vLLM for heavy computation (long-horizon, code gen, evolution)
    - SGLang for real-time interaction (chat, quick responses)

    Provides health monitoring, automatic failover, and load stats.
    """

    # Task type → preferred backend mapping
    BACKEND_PREFERENCES: dict[TaskType, InferenceBackend] = {
        TaskType.LONG_HORIZON: InferenceBackend.VLLM,
        TaskType.REALTIME: InferenceBackend.SGLANG,
        TaskType.TOOL_CALLING: InferenceBackend.VLLM,
        TaskType.EVOLUTION: InferenceBackend.VLLM,
        TaskType.CODE_GENERATION: InferenceBackend.VLLM,
    }

    def __init__(self) -> None:
        self._backends: dict[InferenceBackend, BackendStatus] = {
            InferenceBackend.VLLM: BackendStatus(
                backend=InferenceBackend.VLLM,
                url=os.environ.get("GLM51_VLLM_URL", "http://localhost:8100/v1"),
            ),
            InferenceBackend.SGLANG: BackendStatus(
                backend=InferenceBackend.SGLANG,
                url=os.environ.get("GLM51_SGLANG_URL", "http://localhost:30000/v1"),
            ),
        }
        self._health_check_interval = 30.0  # seconds
        self._monitoring = False

    async def get_backend_url(self, task_type: TaskType = TaskType.REALTIME) -> str:
        """Get the optimal backend URL for the given task type.

        Falls back to the other backend if the preferred one is unhealthy.
        """
        preferred = self.BACKEND_PREFERENCES.get(task_type, InferenceBackend.VLLM)
        status = self._backends[preferred]

        if status.healthy:
            return status.url

        # Try the other backend
        fallback = (
            InferenceBackend.SGLANG if preferred == InferenceBackend.VLLM
            else InferenceBackend.VLLM
        )
        fallback_status = self._backends[fallback]
        if fallback_status.healthy:
            log.info("inference.fallback", preferred=preferred.value, using=fallback.value)
            return fallback_status.url

        # Neither healthy — return preferred anyway (caller handles error)
        return status.url

    async def check_health(self, backend: InferenceBackend | None = None) -> dict[str, Any]:
        """Check health of one or all backends."""
        targets = [backend] if backend else list(self._backends.keys())
        results = {}

        for be in targets:
            status = self._backends[be]
            start = time.time()
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"{status.url}/models")
                    if resp.status_code == 200:
                        status.healthy = True
                        status.latency_ms = (time.time() - start) * 1000
                    else:
                        status.healthy = False
                        status.errors += 1
            except Exception:
                status.healthy = False
                status.errors += 1
                status.latency_ms = 0.0

            status.last_check = time.time()
            results[be.value] = {
                "healthy": status.healthy,
                "url": status.url,
                "latency_ms": round(status.latency_ms, 2),
                "requests_served": status.requests_served,
                "errors": status.errors,
            }

        return results

    def record_request(self, backend: InferenceBackend) -> None:
        """Record a successful request to a backend."""
        self._backends[backend].requests_served += 1

    def record_error(self, backend: InferenceBackend) -> None:
        """Record an error from a backend."""
        self._backends[backend].errors += 1

    async def start_health_monitoring(self) -> None:
        """Start background health monitoring loop."""
        if self._monitoring:
            return
        self._monitoring = True
        asyncio.create_task(self._health_loop())

    async def _health_loop(self) -> None:
        """Background loop checking backend health periodically."""
        while self._monitoring:
            await self.check_health()
            await asyncio.sleep(self._health_check_interval)

    def stop_health_monitoring(self) -> None:
        self._monitoring = False

    def get_status(self) -> dict[str, Any]:
        """Get full status of all backends."""
        return {
            "backends": {
                be.value: {
                    "url": status.url,
                    "healthy": status.healthy,
                    "latency_ms": round(status.latency_ms, 2),
                    "requests_served": status.requests_served,
                    "errors": status.errors,
                    "last_check": status.last_check,
                }
                for be, status in self._backends.items()
            },
            "task_routing": {
                tt.value: be.value
                for tt, be in self.BACKEND_PREFERENCES.items()
            },
            "monitoring_active": self._monitoring,
        }

    def select_backend_for_task(self, task_description: str) -> TaskType:
        """Classify a task description into a TaskType for routing."""
        description_lower = task_description.lower()

        if any(kw in description_lower for kw in ["build system", "8 hour", "long horizon", "overnight"]):
            return TaskType.LONG_HORIZON
        elif any(kw in description_lower for kw in ["evolve", "iteration", "self-improve", "optimize"]):
            return TaskType.EVOLUTION
        elif any(kw in description_lower for kw in ["generate code", "write code", "implement", "create file"]):
            return TaskType.CODE_GENERATION
        elif any(kw in description_lower for kw in ["tool", "execute", "run", "call"]):
            return TaskType.TOOL_CALLING
        else:
            return TaskType.REALTIME
