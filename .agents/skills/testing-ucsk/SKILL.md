---
name: testing-ucsk
description: End-to-end testing procedure for the UCSK (Unified Cognitive Singularity Kernel) scaffold. Use when verifying backend API, WebSocket guidance, agent orchestration, or frontend UI adaptation.
---

# Testing UCSK

## Prerequisites

### Python Dependencies (Backend)
```bash
pip install fastapi uvicorn[standard] python-multipart websockets pydantic pydantic-settings python-dotenv httpx orjson structlog scikit-learn numpy langgraph langchain redis opencv-python-headless mediapipe==0.10.21 sqlalchemy asyncpg qdrant-client neo4j stripe
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

The Vite dev server proxies `/api` to `http://localhost:8000` and `/ws` to `ws://localhost:8000` (configured in `frontend/vite.config.js`).

The backend will log `ucsk.db_init_skipped` on startup if PostgreSQL is not available — this is expected for local testing. All API endpoints still function with in-memory/fallback data.

## Key Backend Endpoints to Test

| Endpoint | Method | Purpose | Expected Response |
|----------|--------|---------|-------------------|
| `/health` | GET | Health check | `{"status":"ok","service":"UCSK"}` |
| `/api/system/info` | GET | System architecture | 6 layers, 13 agents, 5 UI modes, 12 features |
| `/api/sensing/behavior` | POST | Record events | Accepts keystroke/mouse/scroll/click |
| `/api/sensing/state` | GET | Mental state | `{state, confidence, focus, fatigue, ...}` |
| `/api/agents/run` | POST | Run orchestrator | `messages` array from supervisors + specialists |
| `/api/agents/status` | GET | Agent mesh status | 5 supervisors + 8 specialists, total=13, status=ready |
| `/api/billing/plans` | GET | Subscription plans | 3 plans: free ($0), pro ($49), enterprise ($199) with `price_monthly_cents` |
| `/api/billing/revenue` | GET | Revenue summary | `mrr_cents`, `mrr_dollars`, `active_subscriptions` |
| `/api/governance/constitution` | GET | Constitutional rules | 8 rules with severity (critical/high/medium) |
| `/api/governance/audit` | GET | Audit trail | `entries` array + `total` count |
| `/api/governance/privacy/budget/{user_id}` | GET | Privacy budget | `epsilon_total=1.0`, `epsilon_remaining`, `exhausted` |
| `/api/enterprise/dashboard/{team_id}` | GET | Team dashboard | `total_members`, metrics (productivity/creativity/cohesion/focus_index) |
| `/api/enterprise/leaderboard/{team_id}` | GET | Leaderboard | Anonymous entries with `capability_index`, `growth`, `top_dimension` |
| `/api/enterprise/career/{user_id}` | GET | Career simulator | `current_level`, `strongest_domain`, `growth_velocity`, `recommendations` |
| `/api/evaluation/profile/{user_id}` | GET | Capability profile | 5 dimensions: learning_speed, engineering_depth, execution_capability, continuous_evolution, integration_quality |
| `/api/twin/fingerprint/{user_id}` | GET | Digital twin | `languages`, `decision_style`, `learning_velocity`, `total_sessions` |
| `/api/twin/compete/stats/{user_id}` | GET | Compete stats | `total_rounds`, `user_wins`, `twin_wins`, `win_rate` |
| `/api/preferences/config/{user_id}` | GET | Learned prefs | `verbosity_level`, `code_completion_enabled`, etc. |
| `/ws/guidance` | WS | Real-time guidance | state + directive messages |
| `/docs` | GET | Swagger UI | All endpoints documented |

## Frontend Pages to Test

All 11 pages are accessible via the NavBar at the top of the app:

| Route | Page | What to Verify |
|-------|------|----------------|
| `/` | Workspace | Monaco editor, Agent Suggestions panel, Focus/Fatigue/Engagement bars |
| `/dashboard` | Cognitive Dashboard | 4 metric cards (Mental State, Confidence, UI Mode, Capability Index), 5 capability dimension bars, 6 architecture layers, 12 features |
| `/training` | Training Scenarios | Domain selector (6 options), difficulty selector (4 levels), Generate Scenario button produces a scenario card with title, badges, objectives |
| `/compete` | Competitive Twin | Your Record (5 stats: Wins, Twin Wins, Ties, Win Rate, Streak), Challenge Arena with New Challenge button |
| `/twin` | Digital Twin | Skill Fingerprint (Sessions, Patterns, Learning Velocity, Decision Style), Behavioral Prediction, Capture Activity + Export Digital Soul buttons |
| `/career` | Career Simulator | 3 metric cards (Current Level, Strongest Domain, Growth Velocity), Recommendations list |
| `/enterprise` | Enterprise Dashboard | Team selector dropdown, Team Size card, 4 metric bars (productivity/creativity/cohesion/focus_index), anonymous leaderboard table |
| `/research` | Research Intelligence | arXiv search bar with Search button, Trending GitHub Repositories list with star counts and language badges |
| `/governance` | Governance & Ethics | Privacy budget (epsilon remaining/spent/status), Ethical Constitution (8 rules with severity), Audit Trail |
| `/billing` | Billing | Current Plan badge, 3 plan cards (Free $0, Pro $49, Enterprise $199) with features, Revenue Summary (MRR + Active Subs) |
| `/settings` | Settings | 4 consent toggles (Camera, Microphone, Keyboard/Mouse, Skill Sharing), Learned Preferences table |

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

## Known Issues

- **Settings page:** The `code_style` learned preference renders as `[object Object]` because it's a nested object (indentation, quote_style, line_length, docstring_style). Needs `JSON.stringify()` or explicit field rendering.
- Without Docker Compose stack (Qdrant, Neo4j, PostgreSQL, Redis), memory layer endpoints return connection errors but API structure is still verified.
- Face/voice analysis requires camera/microphone hardware + heavy ML deps (torch, whisper). Behavior-only testing path works without these.
- The frontend WebSocket connects to `ws://localhost:8000/ws/guidance` — if backend isn't running, the frontend will show default "idle" state and auto-reconnect every 2s.
- The mental state in the NavBar may change from "idle" to "distracted" during testing as the app detects mouse/keyboard behavior. This is expected behavior, not a bug.

## Devin Secrets Needed

None required for basic testing. Optional:
- `UCSK_GEMINI_API_KEY` — needed only for `/api/memory/skill-diff/generate` endpoint (Gemini-powered skill diff generation)
