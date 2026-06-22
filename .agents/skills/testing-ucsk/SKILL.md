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

### C Library Compilation (Agent Expansion)
```bash
cd backend/agents/c_libs && make all
```
This produces 5 shared libraries in `backend/agents/c_libs/lib/`:
- `librecon.so` — TCP port scanning
- `libvuln.so` — CVE vulnerability analysis
- `libexploit.so` — Safe exploit simulation
- `libtrading.so` — Technical analysis (RSI, MACD, Bollinger)
- `libportfolio.so` — Markowitz portfolio optimization

If `.so` files are missing, endpoints return HTTP 503 with "FileNotFoundError".

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

### Core Endpoints (Layer 0-1)

| Endpoint | Method | Purpose | Expected Response |
|----------|--------|---------|-------------------|
| `/health` | GET | Health check | `{"status":"ok","service":"UCSK"}` |
| `/api/system/info` | GET | System architecture | 6 layers, 40+ agents, 5 UI modes, 20 features |
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

### Agent Expansion Endpoints (Layer 2-3)

| Endpoint | Method | Purpose | Expected Response |
|----------|--------|---------|-------------------|
| `/api/security/scan` | POST | C-based port scan | `{target, open_ports_count, ports: [{port, service, state}]}` |
| `/api/security/vulnerabilities` | POST | CVE correlation | `{vulnerabilities_found, vulnerabilities: [{cve_id, cvss_score, severity}], risk_level}` |
| `/api/security/exploit/simulate` | POST | Safe exploit sim | `{cve_id, success, payload_type, remediation}` |
| `/api/security/assessment` | POST | Full pipeline | `{reconnaissance, vulnerabilities, exploit_simulation, report}` |
| `/api/finance/signals` | POST | Trading signals | `{signal: BUY/SELL/HOLD, indicators: {rsi, sma20, macd, bb_*}, bullish_count}` |
| `/api/finance/backtest` | POST | Strategy backtest | `{initial_capital, final_capital, total_return_pct, win_rate}` |
| `/api/finance/portfolio/optimize` | POST | Markowitz opt | `{allocations, sharpe_ratio, expected_return}` |
| `/api/finance/risk/assess` | POST | VaR calculation | `{var_95, var_99, risk_level, recommendations}` |
| `/api/finance/strategy/execute` | POST | Full strategy | `{analysis, decision, position_sizing, risk_check}` |
| `/api/research-ops/scan` | POST | arXiv scan | `{papers: [...], count, stats}` |
| `/api/research-ops/extract` | POST | Knowledge extraction | `{key_points, methodology, applicability, confidence}` |
| `/api/research-ops/evolve` | POST | Self-evolution | `{cycle, improvements, memory_updated}` |
| `/api/research-ops/stats` | GET | Research stats | `{scanner: {...}, evolver: {...}}` |
| `/api/software/generate` | POST | Code generation | `{task_id, code, agent_used, review}` |
| `/api/software/review` | POST | Code review | `{findings, quality_score, suggestions}` |
| `/api/software/security-review` | POST | OWASP review | `{findings: [{type, severity, pattern}], risk_score}` |
| `/api/software/stats` | GET | Agent stats | 9 agents with success_rate, tasks_completed |
| `/api/negotiation/start` | POST | Start session | `{id, parties, topic, status: "active", analysis}` |
| `/api/negotiation/round` | POST | Negotiate round | `{round_number, proposals, counter_proposals, consensus_reached}` |
| `/api/negotiation/resolve` | POST | Conflict resolution | `{resolution, satisfaction_scores, compromise_areas}` |
| `/api/negotiation/contract/draft` | POST | Draft contract | `{contract_type, sections, parties, terms}` |
| `/api/negotiation/contract/review` | POST | Review contract | `{risks, issues, recommendations, risk_score}` |
| `/api/delivery/plan` | POST | Requirements analysis | `{requirements, architecture, risk_assessment}` |
| `/api/delivery/sprint` | POST | Sprint planning | `{sprint_plan, tasks, duration, team_size}` |
| `/api/delivery/execute` | POST | Task execution | `{task_id, status, result, execution_time}` |
| `/api/delivery/pipeline` | POST | Pipeline execution | `{results: [...], total_time, success_rate}` |
| `/api/delivery/git/status` | GET | Git status | `{branch, modified_files, files, clean}` |
| `/api/delivery/docker/containers` | GET | Docker containers | `{containers: [...], total}` |

## Testing Agent Expansion (curl examples)

### Finance Signals (C-backed)
```bash
curl -X POST http://localhost:8000/api/finance/signals \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"TEST","prices":[100,101,102,100,103,104,102,105,106,104,107,108,106,109,110,108,111,112,110,113,114,112,115,116,114,117,118,116,119,120,118,121,122,120,123,124,122,125,126,124,127,128,126,129,130,128,131,132,130,133]}'
```
**Critical assertions:** `rsi` is between 0-100 and NOT 0, `bb_upper > bb_middle > bb_lower`, signal is BUY/SELL/HOLD.

### Security Vulnerability Analysis (C-backed)
```bash
curl -X POST http://localhost:8000/api/security/vulnerabilities \
  -H 'Content-Type: application/json' \
  -d '{"service":"ssh","banner":"OpenSSH_7.4","port":22}'
```
**Critical assertions:** `vulnerabilities_found >= 1`, first CVE starts with "CVE-", `cvss_score > 0`.

### Full Security Assessment (C pipeline)
```bash
curl -X POST http://localhost:8000/api/security/assessment \
  -H 'Content-Type: application/json' \
  -d '{"target_ip":"127.0.0.1"}'
```
**Critical assertions:** Response has all 4 stages (reconnaissance, vulnerabilities, exploit_simulation, report). Report has `target`, `open_ports`, `risk_score` (0-10).

**Note:** This performs a REAL TCP port scan of the target. Testing against 127.0.0.1 is safe (scans localhost). It will find whatever ports are actually open on the machine (commonly SSH:22 and the backend itself on :8000).

### MoE Routing (Python)
```python
from backend.training.moe_router import MoERouter
router = MoERouter()
assert router.route("SQL injection fix")["routed_to"] == "security"
assert router.route("React component")["routed_to"] == "software"
assert router.route("trading signal AAPL")["routed_to"] == "trading"
```

### Security Code Review
```bash
curl -X POST http://localhost:8000/api/software/security-review \
  -H 'Content-Type: application/json' \
  -d '{"code":"def q(x):\n    return f\"SELECT * FROM t WHERE id={x}\"","language":"python"}'
```
**Critical assertions:** `findings` contains at least one entry with type containing "injection".

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

## Frontend Pages to Test

All 11 pages are accessible via the NavBar at the top of the app:

| Route | Page | What to Verify |
|-------|------|----------------|
| `/` | Workspace | Monaco editor, Agent Suggestions panel, Focus/Fatigue/Engagement bars |
| `/dashboard` | Cognitive Dashboard | 4 metric cards (Mental State, Confidence, UI Mode, Capability Index), 5 capability dimension bars, 6 architecture layers, 20 features |
| `/training` | Training Scenarios | Domain selector (6 options), difficulty selector (4 levels), Generate Scenario button produces a scenario card with title, badges, objectives |
| `/compete` | Competitive Twin | Your Record (5 stats: Wins, Twin Wins, Ties, Win Rate, Streak), Challenge Arena with New Challenge button |
| `/twin` | Digital Twin | Skill Fingerprint (Sessions, Patterns, Learning Velocity, Decision Style), Behavioral Prediction, Capture Activity + Export Digital Soul buttons |
| `/career` | Career Simulator | 3 metric cards (Current Level, Strongest Domain, Growth Velocity), Recommendations list |
| `/enterprise` | Enterprise Dashboard | Team selector dropdown, Team Size card, 4 metric bars (productivity/creativity/cohesion/focus_index), anonymous leaderboard table |
| `/research` | Research Intelligence | arXiv search bar with Search button, Trending GitHub Repositories list with star counts and language badges |
| `/governance` | Governance & Ethics | Privacy budget (epsilon remaining/spent/status), Ethical Constitution (8 rules with severity), Audit Trail |
| `/billing` | Billing | Current Plan badge, 3 plan cards (Free $0, Pro $49, Enterprise $199) with features, Revenue Summary (MRR + Active Subs) |
| `/settings` | Settings | 4 consent toggles (Camera, Microphone, Keyboard/Mouse, Skill Sharing), Learned Preferences table |

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
- The frontend WebSocket connects to `ws://localhost:8000/ws/guidance` — if backend isn't running, the frontend will show default "idle" state and auto-reconnect with exponential backoff (2s → 4s → 8s → 30s max).
- The mental state in the NavBar may change from "idle" to "distracted" during testing as the app detects mouse/keyboard behavior. This is expected behavior, not a bug.
- **Vite proxy error suppression:** The `vite.config.js` overrides `proxy.emit` to intercept ECONNREFUSED errors before Vite's default logger sees it. A simpler `proxy.on("error", ...)` approach does NOT work because Vite registers its own error handler that always logs. For WebSocket proxy errors specifically, the third arg is a raw `net.Socket` (not `ServerResponse`), so `res.writeHead` doesn't exist — must use `res.destroy()` instead.
- **React StrictMode:** Both `useSensing` and `useWebSocket` hooks use a `shouldReconnect` ref. The ref MUST be reset to `true` at the start of the effect body because StrictMode double-invokes effects (cleanup sets it to false, re-run needs it true again).
- **start.sh:** Use `./start.sh` to start both services together. It waits for backend health check before starting frontend, and fails fast if backend doesn't start within 30s.
- **Trading signals require 50+ prices:** For meaningful technical analysis, provide at least 50 data points (needed for SMA50). Fewer than 26 data points will produce incomplete EMA/MACD calculations.
- **Security assessment does REAL TCP scanning:** The `/api/security/assessment` endpoint performs actual network connections. Only test against localhost or owned infrastructure.
- **Gemini fallback:** When `GOOGLE_API_KEY` is not set, agents using Gemini (negotiation, research evolution, software code generation) return placeholder responses. The endpoints still return 200 with valid structure — they don't error out.

## Devin Secrets Needed

None required for basic testing. Optional:
- `UCSK_GEMINI_API_KEY` — needed for full AI-powered responses from negotiation, research evolution, and code generation agents. Without it, these agents use heuristic fallbacks.
