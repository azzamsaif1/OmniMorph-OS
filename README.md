# OmniMorph-OS &middot; UCSK

**Unified Cognitive Singularity Kernel** — an AI-native adaptive cognitive
operating layer that uses multimodal sensing, intelligent agents, and dynamic
interfaces to personalise learning, creativity, and productivity.

> *Project submitted to AI Venture Studio XPRIZE*
> Category: Education & Human Potential + Small Business Services

---

## Architecture (5 Layers)

```
+---------------------------------------------------------+
|  Layer 1 — Sensing & Adaptive Layer                     |
|  MediaPipe Face Mesh, Whisper, keyboard/mouse analytics |
+---------------------------------------------------------+
|  Layer 2 — Cognitive Core                               |
|  State Classifier, Adaptation Engine, Context Manager   |
+---------------------------------------------------------+
|  Layer 3 — Interconnected Agent Mesh                    |
|  5 Supervisors + 8 Specialists (LangGraph orchestrator) |
+---------------------------------------------------------+
|  Layer 4 — Memory & Evolution                           |
|  Qdrant (vectors) + Neo4j (graph) + PostgreSQL (events) |
|  Skill Diff Generator + Federated P2P Learning          |
+---------------------------------------------------------+
|  Layer 5 — Morphing UI                                  |
|  React + Monaco + Three.js + Web Speech + WebHID        |
|  Modes: Visual | Audio | Haptic | Mixed | Zero          |
+---------------------------------------------------------+
```

## 20 Integrated Features

| # | Feature | UCSK Role |
|---|---------|-----------|
| 1 | Core System Architecture (12 Agents) | Central Nervous System |
| 2 | Collective Cognitive Evolution Network | Humanity's Collective Memory |
| 3 | Cognitive Guidance | Neural Mirror System |
| 4 | Supreme Orchestrator & 5 Executive Agents | The Conductor |
| 5 | Adaptive Capability Index & Execution Engine | Maturity Gauge |
| 6 | Autonomous Scientific Research Intelligence | Inquisitive Mind |
| 7 | Autonomous Competitive Engineering Twin | Challenge Partner |
| 8 | Adaptive Cognitive Engineering Environment | Smart Skin |
| 9 | Multi-Agent Autonomous Engineering Ecosystem | Internal Organs |
| 10 | Real-Time Multimodal Cognitive Twin | The Pulse |
| 11 | Digital Engineering Twin | Digital Soul |
| 12 | Competitive Engineering Intelligence | Evolution Race |
| 13 | Self-Adaptive Understanding Layer | System Self-Awareness |
| 14 | Self-Governance & Security Core | Ethical Constitution |
| 15 | Shared Knowledge Civilisation Core | Global Memory Bank |
| 16 | Preference-based Reinforcement Engine | Digital Desires |
| 17 | Long-term Engineering Memory | Lifelong Archive |
| 18 | Real-world Scenario Generator | Challenge Simulator |
| 19 | Career & Professional Evolution Simulator | Future Advisor |
| 20 | Strategic Enterprise Dashboard | Team Operations Room |

## Project Structure

```
ucsk/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Environment settings (pydantic-settings)
│   ├── requirements.txt
│   ├── sensing/                 # Layer 1
│   │   ├── face_analyzer.py     # MediaPipe Face Mesh (468 landmarks)
│   │   ├── voice_analyzer.py    # Whisper + tone analysis
│   │   ├── behavior_analyzer.py # Keystroke / mouse behaviour
│   │   └── mental_state.py      # Sensor fusion → MentalState
│   ├── cognitive/               # Layer 2
│   │   ├── state_classifier.py  # ML classification (GBM)
│   │   ├── adaptation_engine.py # UI & agent adaptation decisions
│   │   └── context_manager.py   # Current work context
│   ├── agents/                  # Layer 3
│   │   ├── orchestrator.py      # LangGraph coordinator
│   │   ├── base.py              # BaseAgent + AgentState
│   │   ├── supervisors/         # 5 high-level agents
│   │   └── specialists/         # 8 domain agents
│   ├── memory/                  # Layer 4
│   │   ├── vector_store.py      # Qdrant client
│   │   ├── graph_store.py       # Neo4j client
│   │   ├── event_store.py       # PostgreSQL + SQLAlchemy
│   │   ├── skill_diff.py        # Gemini-powered Skill Diffs
│   │   └── federated.py         # P2P federated learning
│   ├── api/
│   │   ├── routes/              # REST endpoints
│   │   └── websocket/           # Live guidance WebSocket
│   └── utils/
│       ├── logger.py            # structlog
│       └── security.py          # Privacy helpers
├── frontend/
│   ├── src/
│   │   ├── components/          # 5 UI mode components
│   │   ├── layouts/             # AdaptiveLayout engine
│   │   ├── hooks/               # useSensing, useAdaptation
│   │   └── App.jsx
│   └── package.json
├── infrastructure/
│   ├── docker-compose.yml       # Full local stack
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── k8s/                     # Future K8s manifests
└── docs/
    ├── api_reference.md
    └── user_guide.md
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- Docker & Docker Compose

### 1. Start Infrastructure

```bash
cd infrastructure
docker compose up -d qdrant neo4j postgres redis
```

### 2. Run Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the UI will auto-adapt based on your activity.

### 4. Full Stack (Docker)

```bash
cd infrastructure
docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sensing/frame` | Process camera frame → mental state |
| POST | `/api/sensing/audio` | Process audio clip → mental state |
| POST | `/api/sensing/behavior` | Record keyboard/mouse event |
| GET | `/api/sensing/state` | Get current mental state |
| POST | `/api/agents/run` | Execute orchestrator cycle |
| GET | `/api/agents/status` | Agent mesh health |
| POST | `/api/memory/events` | Record event |
| GET | `/api/memory/events/{user_id}` | Get user events |
| POST | `/api/memory/search` | Semantic search |
| POST | `/api/memory/skill-diff/generate` | Generate Skill Diff |
| GET | `/api/enterprise/dashboard/{team_id}` | Team metrics |
| WS | `/ws/guidance` | Live cognitive guidance stream |

## Technologies

| Category | Stack |
|----------|-------|
| Backend | FastAPI, Python 3.12, Pydantic |
| AI/ML | Gemini API, Whisper, MediaPipe, scikit-learn, PyTorch |
| Agents | LangGraph, LangChain |
| Databases | Qdrant (vector), Neo4j (graph), PostgreSQL (events) |
| Messaging | Redis, WebSocket |
| Frontend | React 19, Vite, Monaco Editor, Three.js, Web Speech API |
| P2P | aiortc (WebRTC data channels) |
| Infrastructure | Docker, Docker Compose |

## License

MIT
