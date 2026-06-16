"""Sensing API — receives camera / audio / behaviour data from the frontend."""

from __future__ import annotations

import base64
from typing import Any

import numpy as np
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from backend.sensing.behavior_analyzer import BehaviorAnalyzer, BehaviorMetrics
from backend.sensing.face_analyzer import FaceAnalyzer
from backend.sensing.mental_state import MentalStateFuser
from backend.sensing.voice_analyzer import VoiceAnalyzer

router = APIRouter()

# Shared instances (per-process singletons)
_face = FaceAnalyzer()
_voice = VoiceAnalyzer()
_behavior = BehaviorAnalyzer()
_fuser = MentalStateFuser()


class FramePayload(BaseModel):
    image_b64: str  # Base64-encoded JPEG/PNG frame


class BehaviorEvent(BaseModel):
    event_type: str  # "keystroke" | "mouse_move" | "scroll" | "click"
    key: str | None = None
    x: float | None = None
    y: float | None = None


class MentalStateResponse(BaseModel):
    state: str
    confidence: float
    focus_score: float
    fatigue_score: float
    frustration_score: float
    engagement_score: float


@router.post("/frame", response_model=MentalStateResponse)
async def process_frame(payload: FramePayload) -> dict[str, Any]:
    """Receive a single camera frame, return the fused mental state."""
    img_bytes = base64.b64decode(payload.image_b64)
    arr = np.frombuffer(img_bytes, dtype=np.uint8)

    import cv2

    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        return MentalStateResponse(
            state="idle", confidence=0, focus_score=0,
            fatigue_score=0, frustration_score=0, engagement_score=0,
        ).model_dump()

    face_metrics = _face.analyze_frame(frame)
    behavior_metrics = _behavior.compute_metrics()
    ms = _fuser.fuse(face=face_metrics, behavior=behavior_metrics)

    return MentalStateResponse(
        state=ms.state.value,
        confidence=ms.confidence,
        focus_score=ms.focus_score,
        fatigue_score=ms.fatigue_score,
        frustration_score=ms.frustration_score,
        engagement_score=ms.engagement_score,
    ).model_dump()


@router.post("/audio", response_model=MentalStateResponse)
async def process_audio(file: UploadFile = File(...)) -> dict[str, Any]:
    """Receive an audio clip, transcribe + analyse, return mental state."""
    data = await file.read()
    audio = np.frombuffer(data, dtype=np.float32)
    voice_metrics = _voice.analyze_audio(audio)
    behavior_metrics = _behavior.compute_metrics()
    ms = _fuser.fuse(voice=voice_metrics, behavior=behavior_metrics)

    return MentalStateResponse(
        state=ms.state.value,
        confidence=ms.confidence,
        focus_score=ms.focus_score,
        fatigue_score=ms.fatigue_score,
        frustration_score=ms.frustration_score,
        engagement_score=ms.engagement_score,
    ).model_dump()


@router.post("/behavior")
async def record_behavior(event: BehaviorEvent) -> dict[str, str]:
    """Ingest a keyboard / mouse / scroll / click event."""
    if event.event_type == "keystroke" and event.key:
        _behavior.record_keystroke(event.key)
    elif event.event_type == "mouse_move" and event.x is not None:
        _behavior.record_mouse_move(event.x, event.y or 0)
    elif event.event_type == "scroll":
        _behavior.record_scroll()
    elif event.event_type == "click":
        _behavior.record_click()
    return {"status": "recorded"}


@router.get("/state", response_model=MentalStateResponse)
async def get_current_state() -> dict[str, Any]:
    """Return the latest fused state from behaviour signals only."""
    behavior_metrics = _behavior.compute_metrics()
    ms = _fuser.fuse(behavior=behavior_metrics)
    return MentalStateResponse(
        state=ms.state.value,
        confidence=ms.confidence,
        focus_score=ms.focus_score,
        fatigue_score=ms.fatigue_score,
        frustration_score=ms.frustration_score,
        engagement_score=ms.engagement_score,
    ).model_dump()
