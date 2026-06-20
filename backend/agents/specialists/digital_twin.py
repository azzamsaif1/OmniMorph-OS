"""Digital Twin Engine — Complete Engineering Mind Clone (Feature 11).

Creates a portable clone of the user's engineering mind by capturing
behavioural patterns, skill fingerprints, decision history, and
coding style into a vector-based digital soul.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from backend.config import settings
from backend.utils.logger import log


@dataclass
class CodingPattern:
    """A single observed coding behaviour pattern."""

    pattern_type: str  # "error_fix", "refactor", "design_choice", "debug_strategy"
    description: str
    context: str
    frequency: int = 1
    last_seen: float = field(default_factory=time.time)
    embedding: list[float] = field(default_factory=list)


@dataclass
class SkillFingerprint:
    """Multi-dimensional profile of a user's engineering skills."""

    user_id: str
    languages: dict[str, float] = field(default_factory=dict)
    frameworks: dict[str, float] = field(default_factory=dict)
    patterns: list[CodingPattern] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    decision_style: str = "balanced"
    error_tendencies: dict[str, int] = field(default_factory=dict)
    learning_velocity: float = 0.5
    total_sessions: int = 0
    total_code_written: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_vector(self) -> list[float]:
        """Convert fingerprint to a dense vector for similarity search."""
        vec: list[float] = []
        top_langs = sorted(self.languages.values(), reverse=True)[:10]
        vec.extend(top_langs + [0.0] * (10 - len(top_langs)))
        top_fw = sorted(self.frameworks.values(), reverse=True)[:10]
        vec.extend(top_fw + [0.0] * (10 - len(top_fw)))
        vec.append(self.learning_velocity)
        vec.append(len(self.strengths) / 20.0)
        vec.append(len(self.weaknesses) / 20.0)
        vec.append(min(self.total_sessions / 1000.0, 1.0))
        return vec

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "decision_style": self.decision_style,
            "learning_velocity": self.learning_velocity,
            "total_sessions": self.total_sessions,
            "pattern_count": len(self.patterns),
        }


@dataclass
class DigitalSoul:
    """Complete exportable digital twin."""

    soul_id: str
    user_id: str
    fingerprint: SkillFingerprint
    version: str = "1.0"
    exported_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "soul_id": self.soul_id,
            "version": self.version,
            "fingerprint": self.fingerprint.to_dict(),
            "exported_at": self.exported_at,
        }

    def to_portable(self) -> str:
        """Serialize to a portable JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class DigitalTwinEngine:
    """Manages digital twin creation, evolution, and export."""

    def __init__(self) -> None:
        self._fingerprints: dict[str, SkillFingerprint] = {}

    def get_or_create(self, user_id: str) -> SkillFingerprint:
        if user_id not in self._fingerprints:
            self._fingerprints[user_id] = SkillFingerprint(user_id=user_id)
        return self._fingerprints[user_id]

    def capture_activity(
        self,
        user_id: str,
        language: str = "",
        framework: str = "",
        pattern_type: str = "",
        pattern_desc: str = "",
        context: str = "",
    ) -> SkillFingerprint:
        fp = self.get_or_create(user_id)
        if language:
            fp.languages[language] = fp.languages.get(language, 0.0) + 0.1
        if framework:
            fp.frameworks[framework] = fp.frameworks.get(framework, 0.0) + 0.1
        if pattern_type and pattern_desc:
            existing = next(
                (p for p in fp.patterns if p.description == pattern_desc), None
            )
            if existing:
                existing.frequency += 1
                existing.last_seen = time.time()
            else:
                fp.patterns.append(
                    CodingPattern(
                        pattern_type=pattern_type,
                        description=pattern_desc,
                        context=context,
                    )
                )
        fp.total_sessions += 1
        fp.updated_at = time.time()
        log.debug("digital_twin.activity_captured", user=user_id)
        return fp

    def record_error(self, user_id: str, error_type: str) -> None:
        fp = self.get_or_create(user_id)
        fp.error_tendencies[error_type] = fp.error_tendencies.get(error_type, 0) + 1

    def update_strengths(self, user_id: str, strengths: list[str], weaknesses: list[str]) -> None:
        fp = self.get_or_create(user_id)
        for s in strengths:
            if s not in fp.strengths:
                fp.strengths.append(s)
        for w in weaknesses:
            if w not in fp.weaknesses:
                fp.weaknesses.append(w)

    def predict_behavior(self, user_id: str, context: dict[str, Any]) -> dict[str, Any]:
        fp = self.get_or_create(user_id)
        top_lang = max(fp.languages, key=fp.languages.get) if fp.languages else "python"
        top_fw = max(fp.frameworks, key=fp.frameworks.get) if fp.frameworks else "unknown"
        recent_patterns = sorted(fp.patterns, key=lambda p: p.last_seen, reverse=True)[:5]

        return {
            "predicted_language": top_lang,
            "predicted_framework": top_fw,
            "likely_patterns": [p.description for p in recent_patterns],
            "error_prone_areas": sorted(
                fp.error_tendencies.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "confidence": min(0.5 + fp.total_sessions * 0.01, 0.95),
        }

    def export_soul(self, user_id: str) -> DigitalSoul:
        fp = self.get_or_create(user_id)
        soul = DigitalSoul(
            soul_id=uuid4().hex[:16],
            user_id=user_id,
            fingerprint=fp,
        )
        log.info("digital_twin.exported", user=user_id, soul_id=soul.soul_id)
        return soul

    def import_soul(self, soul_json: str) -> str:
        data = json.loads(soul_json)
        fp_data = data.get("fingerprint", {})
        user_id = fp_data.get("user_id", uuid4().hex[:8])
        fp = self.get_or_create(user_id)
        fp.languages.update(fp_data.get("languages", {}))
        fp.frameworks.update(fp_data.get("frameworks", {}))
        for s in fp_data.get("strengths", []):
            if s not in fp.strengths:
                fp.strengths.append(s)
        log.info("digital_twin.imported", user=user_id)
        return user_id

    def compare_twins(self, user_a: str, user_b: str) -> dict[str, Any]:
        fp_a = self.get_or_create(user_a)
        fp_b = self.get_or_create(user_b)
        shared_langs = set(fp_a.languages) & set(fp_b.languages)
        shared_fw = set(fp_a.frameworks) & set(fp_b.frameworks)
        return {
            "shared_languages": list(shared_langs),
            "shared_frameworks": list(shared_fw),
            "a_unique_strengths": [s for s in fp_a.strengths if s not in fp_b.strengths],
            "b_unique_strengths": [s for s in fp_b.strengths if s not in fp_a.strengths],
            "learning_velocity_diff": fp_a.learning_velocity - fp_b.learning_velocity,
        }
