---
name: testing-ucsk
description: End-to-end testing procedure for the UCSK (Unified Cognitive Singularity Kernel) scaffold. Use when verifying backend API, WebSocket guidance, agent orchestration, or frontend UI adaptation.
---

# Testing UCSK

## Prerequisites

### Python Dependencies (Backend)
```bash
pip install fastapi uvicorn[standard] python-multipart websockets pydantic pydantic-settings python-dotenv httpx orjson structlog scikit-learn numpy langgraph langchain redis opencv-python-headless mediapipe==0.10.21
```

**Important:** mediapipe must be pinned to `0.10.21` — newer versions removed the `mp.solutions` API that `face_analyzer.py` uses at module level.

**Optional heavy deps** (only needed for camera/microphone features):
- `torch` + `openai-whisper` — voice analysis (imported lazily inside methods)
- These are NOT needed for behavior sensing, WebSocket, or agent testing.

### Node Dependencies (Frontend)
```bash
cd frontend && npm install
```

## Starting the Stack

```bash
# Backend (from repo root)
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend && npm run dev
# Serves at http://localhost:5173
```

## Key Endpoints to Test

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check → `{"status":"ok","service":"UCSK"}` |
| `/api/sensing/behavior` | POST | Record keystroke/mouse/scroll/click events |
| `/api/sensing/state` | GET | Get current mental state + confidence |
| `/api/agents/run` | POST | Run full 13-agent orchestrator cycle |
| `/api/agents/status` | GET | Agent mesh status |
| `/ws/guidance` | WS | Real-time behavior → state → directive stream |
| `/docs` | GET | Swagger UI showing all 18 endpoints |

## Testing WebSocket (Python)

```python
import asyncio, json, websockets

async def test_ws():
    async with websockets.connect('ws://localhost:8000/ws/guidance') as ws:
        await ws.send(json.dumps({'type': 'behavior', 'event_type': 'keystroke', 'key': 'a'}))
        state = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        directive = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        assert state['type'] == 'state'
        assert directive['type'] == 'directive'
        assert directive['ui_mode'] in {'visual', 'audio', 'haptic', 'mixed', 'zero'}

asyncio.run(test_ws())
```

## Testing Agent Orchestrator

```bash
curl -X POST http://localhost:8000/api/agents/run \
  -H 'Content-Type: application/json' \
  -d '{"mental_state": "focused", "ui_mode": "visual", "context": {"work_context": {"active_file": {"path": "main.py", "language": "python"}}}, "tasks": [{"type": "code_review", "description": "Review main.py"}]}'
```

Expect: `messages` array with entries from all supervisors (analysis, interface, execution, memory_agent) + dispatched specialist (codereview).

## Frontend UI Modes

The frontend auto-switches between 5 modes based on mental state:
- **visual** (default/focused): Monaco code editor
- **audio** (fatigued/frustrated): Voice guidance panel
- **mixed** (distracted): Editor + voice guidance side-by-side
- **haptic** (frustrated): Vibration feedback indicators
- **zero** (flow/idle): Minimal distraction-free UI

Mode switching has a 2000ms cooldown (hysteresis) to prevent flickering.

## Known Limitations

- Without Docker Compose stack (Qdrant, Neo4j, PostgreSQL, Redis), memory layer endpoints return connection errors but API structure is still verified.
- Face/voice analysis requires camera/microphone hardware + heavy ML deps (torch, whisper). Behavior-only testing path works without these.
- The frontend WebSocket connects to `ws://localhost:8000/ws/guidance` — if backend isn't running, the frontend will show default "idle" state and auto-reconnect every 2s.

## Devin Secrets Needed

None required for basic testing. Optional:
- `UCSK_GEMINI_API_KEY` — needed only for `/api/memory/skill-diff/generate` endpoint (Gemini-powered skill diff generation)
