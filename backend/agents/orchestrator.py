"""Supreme Orchestrator — LangGraph-based coordinator for all 13 agents.

Builds a directed graph where:
  1. Supervisors run first (Sensory → Analysis → Interface → Execution → Memory).
  2. Specialist agents run in parallel on dispatched tasks.
  3. A final consolidation node merges results.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from backend.agents.base import AgentRole, AgentState
from backend.agents.specialists.architecture_agent import ArchitectureAgent
from backend.agents.specialists.backend_agent import BackendAgent
from backend.agents.specialists.codereview_agent import CodeReviewAgent
from backend.agents.specialists.devops_agent import DevOpsAgent
from backend.agents.specialists.lowlevel_agent import LowLevelAgent
from backend.agents.specialists.research_agent import ResearchAgent
from backend.agents.specialists.security_agent import SecurityAgent
from backend.agents.specialists.testing_agent import TestingAgent
from backend.agents.supervisors.analysis_agent import AnalysisAgent
from backend.agents.supervisors.execution_agent import ExecutionAgent
from backend.agents.supervisors.interface_agent import InterfaceAgent
from backend.agents.supervisors.memory_agent import MemoryAgent
from backend.agents.supervisors.sensory_agent import SensoryAgent
from backend.utils.logger import log

# Instantiate all agents
_supervisors = {
    "sensory": SensoryAgent(),
    "analysis": AnalysisAgent(),
    "interface": InterfaceAgent(),
    "execution": ExecutionAgent(),
    "memory": MemoryAgent(),
}

_specialists = {
    "backend": BackendAgent(),
    "lowlevel": LowLevelAgent(),
    "security": SecurityAgent(),
    "research": ResearchAgent(),
    "codereview": CodeReviewAgent(),
    "testing": TestingAgent(),
    "architecture": ArchitectureAgent(),
    "devops": DevOpsAgent(),
}


# -- Node wrappers (sync → async bridge for LangGraph) --------------------

async def _run_sensory(state: dict[str, Any]) -> dict[str, Any]:
    s = AgentState(**state)
    s = await _supervisors["sensory"].process(s)
    return s.__dict__


async def _run_analysis(state: dict[str, Any]) -> dict[str, Any]:
    s = AgentState(**state)
    s = await _supervisors["analysis"].process(s)
    return s.__dict__


async def _run_interface(state: dict[str, Any]) -> dict[str, Any]:
    s = AgentState(**state)
    s = await _supervisors["interface"].process(s)
    return s.__dict__


async def _run_execution(state: dict[str, Any]) -> dict[str, Any]:
    s = AgentState(**state)
    s = await _supervisors["execution"].process(s)
    return s.__dict__


async def _run_memory(state: dict[str, Any]) -> dict[str, Any]:
    s = AgentState(**state)
    s = await _supervisors["memory"].process(s)
    return s.__dict__


async def _run_specialists(state: dict[str, Any]) -> dict[str, Any]:
    """Run all specialists that have dispatched tasks."""
    s = AgentState(**state)
    for agent in _specialists.values():
        s = await agent.process(s)
    return s.__dict__


async def _consolidate(state: dict[str, Any]) -> dict[str, Any]:
    """Final node: merge results, clean up dispatched queue."""
    s = AgentState(**state)
    s.context.pop("dispatched_tasks", None)
    log.info(
        "orchestrator.cycle_complete",
        messages=len(s.messages),
        completed=len(s.completed_tasks),
    )
    return s.__dict__


def _should_run_specialists(state: dict[str, Any]) -> str:
    dispatched = state.get("context", {}).get("dispatched_tasks", [])
    return "specialists" if dispatched else "consolidate"


def build_orchestrator_graph() -> StateGraph:
    """Construct and compile the UCSK agent graph."""
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("sensory", _run_sensory)
    graph.add_node("analysis", _run_analysis)
    graph.add_node("interface", _run_interface)
    graph.add_node("execution", _run_execution)
    graph.add_node("memory", _run_memory)
    graph.add_node("specialists", _run_specialists)
    graph.add_node("consolidate", _consolidate)

    # Supervisor chain
    graph.set_entry_point("sensory")
    graph.add_edge("sensory", "analysis")
    graph.add_edge("analysis", "interface")
    graph.add_edge("interface", "execution")
    graph.add_edge("execution", "memory")

    # Conditional: run specialists only if tasks were dispatched
    graph.add_conditional_edges(
        "memory",
        _should_run_specialists,
        {"specialists": "specialists", "consolidate": "consolidate"},
    )
    graph.add_edge("specialists", "consolidate")
    graph.add_edge("consolidate", END)

    return graph


# Pre-built compiled graph
orchestrator_graph = build_orchestrator_graph()
