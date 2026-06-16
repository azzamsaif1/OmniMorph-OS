# UCSK API Reference

Base URL: `http://localhost:8000`

---

## Sensing API (`/api/sensing`)

### POST `/api/sensing/frame`

Process a single camera frame and return the fused mental state.

**Request Body:**
```json
{
  "image_b64": "<base64-encoded JPEG/PNG>"
}
```

**Response:**
```json
{
  "state": "focused",
  "confidence": 0.85,
  "focus_score": 0.82,
  "fatigue_score": 0.12,
  "frustration_score": 0.05,
  "engagement_score": 0.78
}
```

### POST `/api/sensing/audio`

Upload an audio clip (16 kHz, mono, float32) for transcription and tone analysis.

**Request:** `multipart/form-data` with field `file`.

**Response:** Same schema as `/api/sensing/frame`.

### POST `/api/sensing/behavior`

Record a keyboard / mouse / scroll / click event.

```json
{
  "event_type": "keystroke",
  "key": "a",
  "x": null,
  "y": null
}
```

Event types: `keystroke`, `mouse_move`, `scroll`, `click`.

### GET `/api/sensing/state`

Return the latest fused mental state from behaviour signals.

---

## Agents API (`/api/agents`)

### POST `/api/agents/run`

Execute one full orchestrator cycle through all 13 agents.

**Request:**
```json
{
  "mental_state": "focused",
  "ui_mode": "visual",
  "context": { "work_context": { "active_file": { "path": "main.py", "language": "python" } } },
  "tasks": [{ "type": "code_review", "description": "Review main.py" }]
}
```

**Response:**
```json
{
  "messages": [
    { "sender": "sensory", "content": "[Sensory] State=focused ...", "metadata": {} }
  ],
  "completed_tasks": [...],
  "ui_directive": { "ui_mode": "visual", "theme": "focus-dark", ... },
  "mental_state": "focused",
  "ui_mode": "visual"
}
```

### GET `/api/agents/status`

Returns agent mesh health info (list of supervisors, specialists, total count).

---

## Memory API (`/api/memory`)

### POST `/api/memory/events`

Record an event to the PostgreSQL event store.

```json
{
  "user_id": "user-123",
  "event_type": "error",
  "description": "TypeError in line 42",
  "payload": { "file": "main.py", "line": 42 }
}
```

### GET `/api/memory/events/{user_id}?event_type=error&limit=50`

Retrieve events for a user, optionally filtered by type.

### POST `/api/memory/search`

Semantic search in the Qdrant vector store.

```json
{
  "user_id": "user-123",
  "query": "async error handling",
  "top_k": 5
}
```

### GET `/api/memory/skills/{user_id}`

Return the user's skill graph from Neo4j.

### POST `/api/memory/skill-diff/generate`

Generate a Skill Diff from user evidence via Gemini.

```json
{
  "user_id": "user-123",
  "skill_domain": "async programming",
  "evidence": "User consistently writes correct async/await patterns...",
  "difficulty": 0.5
}
```

### GET `/api/memory/federated/stats`

Return P2P network statistics (peer count, skill diffs, queue size).

---

## Enterprise API (`/api/enterprise`)

### GET `/api/enterprise/dashboard/{team_id}`

Team cognitive metrics dashboard (privacy-safe aggregates).

### GET `/api/enterprise/leaderboard/{team_id}?limit=10`

Anonymous leaderboard based on skill progression.

### POST `/api/enterprise/team/{team_id}/members`

Add a member to a team.

### GET `/api/enterprise/career/{user_id}`

Career evolution simulation based on user capabilities.

### POST `/api/enterprise/scenario/generate?skill_level=intermediate&domain=backend`

Generate a real-world training scenario.

---

## WebSocket (`/ws/guidance`)

Bidirectional WebSocket for live cognitive guidance.

**Client → Server:**
```json
{ "type": "behavior", "event_type": "keystroke", "key": "a" }
{ "type": "query", "text": "help me with this function" }
```

**Server → Client:**
```json
{ "type": "state", "state": "focused", "confidence": 0.85, "focus": 0.82, ... }
{ "type": "directive", "ui_mode": "audio", "theme": "rest-calm", ... }
{ "type": "guidance", "text": "I suggest taking a short break." }
```

---

## Health Check

### GET `/health`

```json
{ "status": "ok", "service": "UCSK" }
```
