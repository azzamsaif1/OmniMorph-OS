"""Live Guidance WebSocket — streams real-time audio / visual guidance.

The frontend connects to ``/ws/guidance`` and receives a continuous
stream of adaptation directives, spoken guidance text, and UI-mode
switch commands. Uses Gemini for contextual guidance.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.cognitive.adaptation_engine import AdaptationEngine
from backend.gemini_client import gemini_guidance
from backend.sensing.behavior_analyzer import BehaviorAnalyzer
from backend.sensing.mental_state import MentalStateFuser
from backend.utils.logger import log

router = APIRouter()


@router.websocket("/guidance")
async def guidance_stream(ws: WebSocket) -> None:
    """Bidirectional WebSocket for live cognitive guidance.

    Client sends:
        {"type": "behavior", "event_type": "keystroke", "key": "a"}
        {"type": "query",   "text": "help me with this function"}

    Server sends:
        {"type": "state",     "state": "focused", "confidence": 0.85, ...}
        {"type": "directive", "ui_mode": "audio", "theme": "rest-calm", ...}
        {"type": "guidance",  "text": "I suggest taking a short break."}
    """
    await ws.accept()
    log.info("ws.guidance.connected")

    behavior = BehaviorAnalyzer()
    fuser = MentalStateFuser()
    engine = AdaptationEngine()
    work_context: dict[str, Any] = {}
    interaction_count = 0

    try:
        while True:
            raw = await ws.receive_text()
            msg: dict[str, Any] = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "behavior":
                etype = msg.get("event_type", "")
                if etype == "keystroke":
                    behavior.record_keystroke(msg.get("key", ""))
                elif etype == "mouse_move":
                    behavior.record_mouse_move(
                        msg.get("x", 0), msg.get("y", 0)
                    )
                elif etype == "scroll":
                    behavior.record_scroll()
                elif etype == "click":
                    behavior.record_click()

                bm = behavior.compute_metrics()
                ms = fuser.fuse(behavior=bm)
                plan = engine.decide(ms.state, ms.confidence)

                await ws.send_json(
                    {
                        "type": "state",
                        "state": ms.state.value,
                        "confidence": round(ms.confidence, 3),
                        "focus": round(ms.focus_score, 3),
                        "fatigue": round(ms.fatigue_score, 3),
                        "frustration": round(ms.frustration_score, 3),
                        "engagement": round(ms.engagement_score, 3),
                    }
                )
                await ws.send_json(
                    {
                        "type": "directive",
                        "ui_mode": plan.ui_mode.value,
                        "theme": plan.ambient_theme,
                        "verbosity": plan.agent_verbosity,
                        "suggestions": plan.suggestions_enabled,
                        "break_reminder": plan.break_reminder,
                    }
                )

                interaction_count += 1
                if interaction_count % 50 == 0 and ms.state.value in ("fatigued", "frustrated"):
                    guidance_text = await gemini_guidance(
                        mental_state=ms.state.value,
                        work_context=work_context,
                    )
                    await ws.send_json(
                        {"type": "guidance", "text": guidance_text}
                    )

            elif msg_type == "query":
                text = msg.get("text", "")
                bm = behavior.compute_metrics()
                ms = fuser.fuse(behavior=bm)

                guidance_text = await gemini_guidance(
                    mental_state=ms.state.value,
                    work_context=work_context,
                    query=text,
                )
                await ws.send_json(
                    {"type": "guidance", "text": guidance_text}
                )

            elif msg_type == "context":
                work_context.update(msg.get("data", {}))

    except WebSocketDisconnect:
        log.info("ws.guidance.disconnected")
    except Exception as exc:
        log.error("ws.guidance.error", error=str(exc))
        await ws.close(code=1011)
