"""Face Analyzer — MediaPipe Face Mesh for 468-landmark extraction.

Extracts facial expressions, eye-gaze direction, blink rate, and
micro-expression indicators that feed into ``MentalState``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import mediapipe as mp
import numpy as np

from backend.utils.logger import log

_mp_face_mesh = mp.solutions.face_mesh


@dataclass
class FaceMetrics:
    """Quantified facial signals for a single frame."""

    blink_rate: float = 0.0
    eye_aspect_ratio_left: float = 0.0
    eye_aspect_ratio_right: float = 0.0
    gaze_direction: tuple[float, float] = (0.0, 0.0)
    mouth_openness: float = 0.0
    eyebrow_raise: float = 0.0
    head_tilt: tuple[float, float, float] = (0.0, 0.0, 0.0)
    expression_valence: float = 0.0  # -1 negative … +1 positive
    raw_landmarks: list[Any] = field(default_factory=list)


# Key landmark indices (MediaPipe 468-point topology)
_LEFT_EYE = [362, 385, 387, 263, 373, 380]
_RIGHT_EYE = [33, 160, 158, 133, 153, 144]
_LIPS_OUTER = [61, 291, 0, 17]


def _eye_aspect_ratio(landmarks: np.ndarray, indices: list[int]) -> float:
    pts = landmarks[indices]
    vertical_a = np.linalg.norm(pts[1] - pts[5])
    vertical_b = np.linalg.norm(pts[2] - pts[4])
    horizontal = np.linalg.norm(pts[0] - pts[3])
    if horizontal == 0:
        return 0.0
    return float((vertical_a + vertical_b) / (2.0 * horizontal))


class FaceAnalyzer:
    """Wraps MediaPipe Face Mesh and computes per-frame ``FaceMetrics``."""

    def __init__(self, max_faces: int = 1, min_confidence: float = 0.5) -> None:
        self._mesh = _mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_faces,
            refine_landmarks=True,
            min_detection_confidence=min_confidence,
            min_tracking_confidence=min_confidence,
        )
        self._blink_counter: int = 0
        self._frame_counter: int = 0
        self._blink_threshold: float = 0.21

    def analyze_frame(self, bgr_frame: np.ndarray) -> FaceMetrics | None:
        """Process a single BGR frame; return ``FaceMetrics`` or *None*."""
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        result = self._mesh.process(rgb)
        if not result.multi_face_landmarks:
            return None

        face = result.multi_face_landmarks[0]
        h, w, _ = bgr_frame.shape
        lm = np.array([(p.x * w, p.y * h, p.z * w) for p in face.landmark])

        ear_l = _eye_aspect_ratio(lm, _LEFT_EYE)
        ear_r = _eye_aspect_ratio(lm, _RIGHT_EYE)

        self._frame_counter += 1
        if (ear_l + ear_r) / 2 < self._blink_threshold:
            self._blink_counter += 1

        blink_rate = (
            self._blink_counter / (self._frame_counter / 30.0)
            if self._frame_counter > 0
            else 0.0
        )

        # Mouth openness (normalised)
        lip_pts = lm[_LIPS_OUTER]
        mouth_open = float(np.linalg.norm(lip_pts[2] - lip_pts[3]))
        mouth_width = float(np.linalg.norm(lip_pts[0] - lip_pts[1]))
        mouth_ratio = mouth_open / mouth_width if mouth_width > 0 else 0.0

        # Gaze approximation via iris offset from eye centre
        gaze_x = float(lm[468][0] - lm[473][0]) if len(lm) > 473 else 0.0
        gaze_y = float(lm[468][1] - lm[473][1]) if len(lm) > 473 else 0.0

        # Head pose (simplified pitch/yaw/roll from nose + forehead)
        nose = lm[1]
        forehead = lm[10]
        chin = lm[152]
        pitch = float(np.arctan2(chin[1] - forehead[1], chin[2] - forehead[2]))
        yaw = float(np.arctan2(nose[0] - lm[454][0], nose[2] - lm[454][2]))
        roll = float(np.arctan2(lm[33][1] - lm[263][1], lm[33][0] - lm[263][0]))

        # Simple valence: eyebrow raise + smile proxy
        brow = float(lm[9][1] - lm[10][1])
        valence = float(np.clip((mouth_ratio - 0.3) + (brow * 0.01), -1, 1))

        metrics = FaceMetrics(
            blink_rate=blink_rate,
            eye_aspect_ratio_left=ear_l,
            eye_aspect_ratio_right=ear_r,
            gaze_direction=(gaze_x, gaze_y),
            mouth_openness=mouth_ratio,
            eyebrow_raise=brow,
            head_tilt=(pitch, yaw, roll),
            expression_valence=valence,
            raw_landmarks=lm.tolist(),
        )
        log.debug("face.metrics", blink_rate=blink_rate, ear_l=ear_l, ear_r=ear_r)
        return metrics

    def reset_counters(self) -> None:
        self._blink_counter = 0
        self._frame_counter = 0

    def close(self) -> None:
        self._mesh.close()
