"""Tests for agent system — base classes, orchestrator, specialists."""

from __future__ import annotations

import pytest

from backend.agents.base import AgentMessage, AgentRole, AgentState


class TestAgentState:
    def test_default_state(self):
        state = AgentState()
        assert state.mental_state == "focused"
        assert state.ui_mode == "visual"
        assert state.messages == []
        assert state.context == {}
        assert state.pending_tasks == []
        assert state.completed_tasks == []

    def test_state_with_context(self):
        state = AgentState(
            mental_state="frustrated",
            ui_mode="audio",
            context={"active_file": "main.py"},
        )
        assert state.mental_state == "frustrated"
        assert state.ui_mode == "audio"
        assert state.context["active_file"] == "main.py"


class TestAgentMessage:
    def test_message_fields(self):
        msg = AgentMessage(
            sender=AgentRole.SECURITY,
            recipient=AgentRole.EXECUTION,
            content="Found vulnerability",
        )
        assert msg.sender == AgentRole.SECURITY
        assert msg.recipient == AgentRole.EXECUTION
        assert msg.content == "Found vulnerability"
        assert len(msg.message_id) == 12

    def test_broadcast_message(self):
        msg = AgentMessage(
            sender=AgentRole.SENSORY,
            recipient=None,
            content="State update",
        )
        assert msg.recipient is None


class TestAgentRoles:
    def test_supervisor_roles(self):
        supervisors = ["sensory", "analysis", "interface", "execution", "memory_agent"]
        for role_val in supervisors:
            assert AgentRole(role_val) is not None

    def test_specialist_roles(self):
        specialists = [
            "backend", "lowlevel", "security", "research",
            "codereview", "testing", "architecture", "devops",
        ]
        for role_val in specialists:
            assert AgentRole(role_val) is not None

    def test_total_roles(self):
        assert len(AgentRole) == 13


@pytest.mark.anyio
async def test_agents_status_api(client):
    resp = await client.get("/api/agents/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_agents"] == 13
    assert len(data["supervisors"]) == 5
    assert len(data["specialists"]) == 8
    assert data["status"] == "ready"
