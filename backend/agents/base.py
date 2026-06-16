"""Base classes shared by all UCSK agents."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    # Supervisors
    SENSORY = "sensory"
    ANALYSIS = "analysis"
    INTERFACE = "interface"
    EXECUTION = "execution"
    MEMORY = "memory_agent"
    # Specialists
    BACKEND = "backend"
    LOWLEVEL = "lowlevel"
    SECURITY = "security"
    RESEARCH = "research"
    CODEREVIEW = "codereview"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    DEVOPS = "devops"


@dataclass
class AgentMessage:
    """Envelope exchanged between agents via the orchestrator."""

    sender: AgentRole
    recipient: AgentRole | None  # None = broadcast
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass
class AgentState:
    """Shared mutable state passed through the LangGraph graph."""

    messages: list[AgentMessage] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    mental_state: str = "focused"
    ui_mode: str = "visual"
    pending_tasks: list[dict[str, Any]] = field(default_factory=list)
    completed_tasks: list[dict[str, Any]] = field(default_factory=list)


class BaseAgent(ABC):
    """Contract every UCSK agent must satisfy."""

    role: AgentRole

    def __init__(self, role: AgentRole) -> None:
        self.role = role

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Receive the shared state, act, and return the updated state."""

    def _emit(
        self,
        state: AgentState,
        content: str,
        recipient: AgentRole | None = None,
        **meta: Any,
    ) -> None:
        state.messages.append(
            AgentMessage(
                sender=self.role,
                recipient=recipient,
                content=content,
                metadata=meta,
            )
        )
