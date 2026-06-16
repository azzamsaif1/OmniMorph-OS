"""Agents API — triggers orchestrator execution and queries agent state."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.base import AgentState
from backend.agents.orchestrator import orchestrator_graph

router = APIRouter()


class RunCycleRequest(BaseModel):
    mental_state: str = "focused"
    ui_mode: str = "visual"
    context: dict[str, Any] = {}
    tasks: list[dict[str, Any]] = []


class RunCycleResponse(BaseModel):
    messages: list[dict[str, Any]]
    completed_tasks: list[dict[str, Any]]
    ui_directive: dict[str, Any] | None = None
    mental_state: str
    ui_mode: str


@router.post("/run", response_model=RunCycleResponse)
async def run_cycle(req: RunCycleRequest) -> dict[str, Any]:
    """Execute one full orchestrator cycle."""
    initial_state = AgentState(
        mental_state=req.mental_state,
        ui_mode=req.ui_mode,
        context=req.context,
        pending_tasks=req.tasks,
    )

    compiled = orchestrator_graph.compile()
    result = await compiled.ainvoke(initial_state.__dict__)

    return RunCycleResponse(
        messages=[
            {"sender": m.sender, "content": m.content, "metadata": m.metadata}
            for m in result.get("messages", [])
            if hasattr(m, "sender")
        ],
        completed_tasks=result.get("completed_tasks", []),
        ui_directive=result.get("context", {}).get("ui_directive"),
        mental_state=result.get("mental_state", "focused"),
        ui_mode=result.get("ui_mode", "visual"),
    ).model_dump()


@router.get("/status")
async def agent_status() -> dict[str, Any]:
    """Return current agent mesh health info."""
    return {
        "supervisors": [
            "sensory", "analysis", "interface", "execution", "memory",
        ],
        "specialists": [
            "backend", "lowlevel", "security", "research",
            "codereview", "testing", "architecture", "devops",
        ],
        "total_agents": 13,
        "status": "ready",
    }
