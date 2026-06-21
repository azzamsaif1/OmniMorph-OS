# OmniMorph-OS &middot; UCSK

**Unified Cognitive Singularity Kernel** — an AI-native cognitive operating layer
that reads your mental state through multimodal sensing, orchestrates 13 AI agents
to assist with engineering tasks, and adapts its interface in real time.

> **Build with Gemini XPRIZE** — Category: Education & Human Potential
>
> See [SUBMISSION.md](SUBMISSION.md) for the full competition narrative.

---

## What It Does

UCSK processes three signal streams simultaneously:

- **Face** — MediaPipe Face Mesh (468 landmarks) detects fatigue, focus, frustration
- **Voice** — Whisper analyses vocal tone for stress indicators
- **Behaviour** — Keystroke speed, correction rate, mouse velocity, idle periods

These fuse into a **Mental State Vector** `[Focus, Fatigue, Frustration, Flow]` that
drives every downstream decision: which UI mode to display, which agents to activate,
and how aggressively the system should intervene. The interface switches between
5 modes (Visual, Audio, Haptic, Mixed, Zero) in under 200ms.

## Architecture (6 Layers)

```
Layer 0  Multimodal Sensing     Face Mesh + Whisper + Behaviour Analytics
Layer 1  Cognitive Kernel       State Classifier + Adaptation Engine (<200ms)
Layer 2  Agent Mesh             5 Supervisors + 8 Specialists (13 total)
Layer 3  Collective Memory      Qdrant + Neo4j + PostgreSQL + Federated Learning
Layer 4  Multi-Morph UI         React 19 + Monaco + Three.js + Web Speech
Layer 5  Cloud Infrastructure   Gemini API + Cloud Run + Stripe
```

All 13 agents are powered by the **Gemini API** (`gemini-2.0-flash`) with automatic
fallback to heuristic responses when the API is unavailable.

## Quick Start

```bash
git clone https://github.com/azzamsaif1/OmniMorph-OS.git
cd OmniMorph-OS

# Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Start both services (backend waits for health check, then starts frontend)
./start.sh

# Or start individually:
uvicorn backend.main:app --host 0.0.0.0 --port 8000   # Backend on :8000
cd frontend && npm run dev                               # Frontend on :5173
```

Open http://localhost:5173 — the UI auto-adapts as you interact.

API documentation: http://localhost:8000/docs

### Run Tests

```bash
python -m pytest backend/tests/ -v    # 81 tests, ~0.6s
```

### Environment Variables (optional)

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_API_KEY` | Gemini API for agent intelligence | Falls back to heuristics |
| `DATABASE_URL` | PostgreSQL connection | In-memory/SQLite fallback |
| `STRIPE_SECRET_KEY` | Billing integration | Mock billing data |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification | Webhooks disabled |

## Project Structure

```
OmniMorph-OS/
├── backend/
│   ├── main.py                    # FastAPI entry point + route registration
│   ├── config.py                  # pydantic-settings configuration
│   ├── gemini_client.py           # Gemini API client with fallback
│   ├── auth.py                    # JWT authentication
│   ├── models.py                  # SQLAlchemy models
│   ├── database.py                # Async DB init
│   ├── sensing/                   # Layer 0: Multimodal sensing
│   │   ├── face_analyzer.py       #   MediaPipe Face Mesh (468 landmarks)
│   │   ├── voice_analyzer.py      #   Whisper + tone analysis
│   │   ├── behavior_analyzer.py   #   Keystroke / mouse / scroll events
│   │   └── mental_state.py        #   Sensor fusion classifier
│   ├── cognitive/                 # Layer 1: Cognitive kernel
│   │   ├── state_classifier.py    #   ML state classification
│   │   ├── adaptation_engine.py   #   UI mode + agent behaviour decisions
│   │   └── context_manager.py     #   Work context tracking
│   ├── agents/                    # Layer 2: Agent mesh
│   │   ├── orchestrator.py        #   LangGraph multi-agent coordinator
│   │   ├── base.py                #   BaseAgent + AgentState
│   │   ├── supervisors/           #   5 supervisory agents
│   │   └── specialists/           #   8 domain specialists + digital twin
│   ├── memory/                    # Layer 3: Collective memory
│   │   ├── vector_store.py        #   Qdrant vector DB
│   │   ├── graph_store.py         #   Neo4j graph DB
│   │   ├── event_store.py         #   PostgreSQL event store
│   │   ├── skill_diff.py          #   Gemini-powered skill extraction
│   │   └── federated.py           #   P2P federated learning (DP epsilon=1.0)
│   ├── governance/                # Constitutional rules + audit
│   ├── evaluation/                # Capability index + benchmarks
│   ├── research/                  # arXiv + GitHub intelligence
│   ├── api/
│   │   ├── routes/                # 12 REST route modules
│   │   └── websocket/guidance.py  # Real-time mental state WebSocket
│   └── tests/                     # 81 pytest tests
├── frontend/
│   ├── src/
│   │   ├── pages/                 # 11 pages (Dashboard, Training, Compete, ...)
│   │   ├── components/            # 5 UI mode components
│   │   ├── layouts/               # AdaptiveLayout engine
│   │   ├── hooks/                 # useSensing, useWebSocket, useAdaptation
│   │   ├── App.jsx                # React Router
│   │   └── index.jsx              # Entry point
│   ├── vite.config.js             # Proxy config with ECONNREFUSED suppression
│   └── package.json
├── start.sh                       # Coordinated startup script
├── pyrightconfig.json             # IDE type checking config
├── SUBMISSION.md                  # Competition submission narrative
└── infrastructure/
    ├── docker-compose.yml
    ├── Dockerfile.backend
    └── Dockerfile.frontend
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/system/info` | Architecture: 6 layers, 13 agents, 20 features |
| POST | `/api/sensing/behavior` | Record keystroke/mouse/scroll/click event |
| GET | `/api/sensing/state` | Current mental state + confidence |
| POST | `/api/agents/run` | Execute multi-agent orchestrator |
| GET | `/api/agents/status` | Agent mesh health (13 agents) |
| GET | `/api/billing/plans` | Subscription plans (Free/Pro/Enterprise) |
| GET | `/api/governance/constitution` | 8 immutable ethical rules |
| GET | `/api/governance/privacy/budget/{user_id}` | Privacy budget (epsilon) |
| GET | `/api/enterprise/dashboard/{team_id}` | Team cognitive analytics |
| GET | `/api/enterprise/career/{user_id}` | Career simulation |
| GET | `/api/twin/fingerprint/{user_id}` | Digital twin export |
| POST | `/api/training/scenarios/generate` | Dynamic training scenarios |
| GET | `/api/evaluation/profile/{user_id}` | 5-dimension capability profile |
| WS | `/ws/guidance` | Real-time mental state + UI directives |

## Technologies

| Category | Stack |
|----------|-------|
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy |
| AI/ML | Gemini API, MediaPipe Face Mesh, Whisper, scikit-learn |
| Agents | LangGraph, LangChain |
| Databases | Qdrant (vector), Neo4j (graph), PostgreSQL (events) |
| Frontend | React 19, Vite 6, Monaco Editor, Three.js, Web Speech API |
| Billing | Stripe (3-tier: Free $0 / Pro $49 / Enterprise $199) |
| Infrastructure | Docker, Docker Compose, Google Cloud Run |
| Testing | pytest (81 tests), pytest-asyncio, httpx |

## 20 Integrated Features

| # | Feature | Implementation |
|---|---------|---------------|
| 1 | Core Architecture (13 Agents) | `agents/orchestrator.py` + supervisors + specialists |
| 2 | Collective Cognitive Evolution | `memory/federated.py` — DP skill transfer |
| 3 | Cognitive Guidance | `sensing/` — face + voice + behaviour fusion |
| 4 | Supreme Orchestrator | `agents/orchestrator.py` — LangGraph coordination |
| 5 | Adaptive Capability Index | `evaluation/capability_index.py` — 5 dimensions |
| 6 | Research Intelligence | `research/` — arXiv + GitHub tracking |
| 7 | Competitive Twin | `specialists/competitive_twin.py` |
| 8 | Adaptive Environment | `layouts/AdaptiveLayout.jsx` — 5 UI modes |
| 9 | Multi-Agent Ecosystem | 8 Gemini-powered specialist agents |
| 10 | Real-Time Cognitive Twin | `/ws/guidance` WebSocket stream |
| 11 | Digital Engineering Twin | `specialists/digital_twin.py` |
| 12 | Competitive Intelligence | `/api/twin/compete/` — anonymous ranking |
| 13 | Self-Adaptive Layer | `cognitive/adaptation_engine.py` |
| 14 | Self-Governance | `governance/` — 8 rules + audit trail |
| 15 | Shared Knowledge Core | Federated learning + Skill Diffs |
| 16 | Preference Engine | `specialists/preference_engine.py` |
| 17 | Long-term Memory | Vector + graph + event stores |
| 18 | Scenario Generator | `/api/training/scenarios/generate` |
| 19 | Career Simulator | `/api/enterprise/career/{user_id}` |
| 20 | Enterprise Dashboard | `/api/enterprise/dashboard/{team_id}` |

## License

MIT
