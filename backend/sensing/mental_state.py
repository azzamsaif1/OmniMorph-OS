"""Sensor Fusion — combines face, voice, and behaviour into a ``MentalState``.

The ``MentalStateFuser`` assigns weights to each modality (configurable)
and emits a single state label with a confidence score, refreshed every
sensing cycle (~50 ms target).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from backend.sensing.behavior_analyzer import BehaviorMetrics
from backend.sensing.face_analyzer import FaceMetrics
from backend.sensing.voice_analyzer import VoiceMetrics
from backend.utils.logger import log


class CognitiveState(str, Enum):
    """Discrete cognitive-state labels."""

    FOCUSED = "focused"
    DISTRACTED = "distracted"
    FATIGUED = "fatigued"
    FRUSTRATED = "frustrated"
    FLOW = "flow"
    IDLE = "idle"


@dataclass
class MentalState:
    """Fused output representing the user's current cognitive state."""

    state: CognitiveState
    confidence: float  # 0..1
    focus_score: float
    fatigue_score: float
    frustration_score: float
    engagement_score: float
    raw_vector: list[float]


class MentalStateFuser:
    """Weighted fusion of face + voice + behaviour metrics."""

    def __init__(
        self,
        w_face: float = 0.45,
        w_voice: float = 0.25,
        w_behavior: float = 0.30,
    ) -> None:
        total = w_face + w_voice + w_behavior
        self._w_face = w_face / total
        self._w_voice = w_voice / total
        self._w_behavior = w_behavior / total

    def fuse(
        self,
        face: FaceMetrics | None = None,
        voice: VoiceMetrics | None = None,
        behavior: BehaviorMetrics | None = None,
    ) -> MentalState:
        # --- Feature extraction per modality ---

        # Face → [focus, fatigue, frustration, engagement]
        if face is not None:
            ear = (face.eye_aspect_ratio_left + face.eye_aspect_ratio_right) / 2
            f_focus = np.clip(ear / 0.3, 0, 1)
            f_fatigue = np.clip(1 - ear / 0.25, 0, 1) * np.clip(
                face.blink_rate / 25, 0, 1
            )
            f_frustration = np.clip(-face.expression_valence, 0, 1)
            f_engagement = np.clip(face.expression_valence + 0.5, 0, 1)
            face_vec = np.array(
                [f_focus, f_fatigue, f_frustration, f_engagement], dtype=np.float64
            )
        else:
            face_vec = np.array([0.5, 0.0, 0.0, 0.5])

        # Voice
        if voice is not None:
            tone_map = {
                "focused": np.array([0.9, 0.1, 0.1, 0.8]),
                "fatigued": np.array([0.3, 0.9, 0.1, 0.2]),
                "frustrated": np.array([0.4, 0.2, 0.9, 0.3]),
                "neutral": np.array([0.5, 0.2, 0.2, 0.5]),
            }
            voice_vec = tone_map.get(
                voice.tone_label, np.array([0.5, 0.2, 0.2, 0.5])
            )
        else:
            voice_vec = np.array([0.5, 0.0, 0.0, 0.5])

        # Behaviour
        if behavior is not None:
            b_focus = np.clip(behavior.activity_score, 0, 1)
            b_fatigue = np.clip(1 - behavior.activity_score, 0, 1) * np.clip(
                behavior.idle_gap_sec / 30, 0, 1
            )
            b_frustration = np.clip(behavior.error_rate / 0.3, 0, 1)
            b_engagement = np.clip(behavior.typing_speed_cpm / 200, 0, 1)
            behav_vec = np.array(
                [b_focus, b_fatigue, b_frustration, b_engagement], dtype=np.float64
            )
        else:
            behav_vec = np.array([0.5, 0.0, 0.0, 0.5])

        # --- Weighted fusion ---
        fused = (
            self._w_face * face_vec
            + self._w_voice * voice_vec
            + self._w_behavior * behav_vec
        )

        focus, fatigue, frustration, engagement = fused.tolist()

        # --- Classification ---
        scores = {
            CognitiveState.FOCUSED: focus * (1 - fatigue),
            CognitiveState.DISTRACTED: (1 - focus) * (1 - frustration),
            CognitiveState.FATIGUED: fatigue,
            CognitiveState.FRUSTRATED: frustration,
            CognitiveState.FLOW: focus * engagement * (1 - fatigue) * (1 - frustration),
            CognitiveState.IDLE: max(0, 1 - focus - engagement),
        }
        best_state = max(scores, key=lambda s: scores[s])
        confidence = float(np.clip(scores[best_state], 0, 1))

        state = MentalState(
            state=best_state,
            confidence=confidence,
            focus_score=float(focus),
            fatigue_score=float(fatigue),
            frustration_score=float(frustration),
            engagement_score=float(engagement),
            raw_vector=fused.tolist(),
        )
        log.debug(
            "mental_state.fused",
            state=best_state.value,
            confidence=round(confidence, 3),
        )
        return state
