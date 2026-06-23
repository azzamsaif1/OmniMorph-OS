"""LLM integration layer for OmniMorph-OS.

Provides multi-model support with GLM-5.1 as the primary self-evolving engine.
Falls back gracefully to existing Gemini integration when GLM-5.1 is unavailable.
"""

from backend.llm.glm_client import GLM51Client
from backend.llm.inference_manager import InferenceManager
from backend.llm.model_registry import ModelRegistry

__all__ = ["GLM51Client", "InferenceManager", "ModelRegistry"]
