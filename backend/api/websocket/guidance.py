"""Live Guidance WebSocket — streams real-time audio / visual guidance.

The frontend connects to ``/ws/guidance`` and receives a continuous
stream of adaptation directives, spoken guidance text, and UI-mode
switch commands.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.cognitive.adaptation_engine import AdaptationEngine
from backend.sensing.behavior_analyzer import BehaviorAnalyzer
from backend.sensing.mental_state import MentalStateFuser
from backend.utils.logger import log

router = APIRouter()

_engine = AdaptationEngine()
_fuser = MentalStateFuser()
_behavior = BehaviorAnalyzer()


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

    try:
        while True:
            raw = await ws.receive_text()
            msg: dict[str, Any] = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "behavior":
                etype = msg.get("event_type", "")
                if etype == "keystroke":
                    _behavior.record_keystroke(msg.get("key", ""))
                elif etype == "mouse_move":
                    _behavior.record_mouse_move(
                        msg.get("x", 0), msg.get("y", 0)
                    )
                elif etype == "scroll":
                    _behavior.record_scroll()
                elif etype == "click":
                    _behavior.record_click()

                # Fuse and send updated state
                bm = _behavior.compute_metrics()
                ms = _fuser.fuse(behavior=bm)
                plan = _engine.decide(ms.state, ms.confidence)

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

            elif msg_type == "query":
                text = msg.get("text", "")
                # Placeholder: real impl calls Gemini for contextual guidance
                await ws.send_json(
                    {
                        "type": "guidance",
                        "text": f"Received your query: '{text}'. "
                        f"Generating response...",
                    }
                )

    except WebSocketDisconnect:
        log.info("ws.guidance.disconnected")
    except Exception as exc:
        log.error("ws.guidance.error", error=str(exc))
        await ws.close(code=1011)
