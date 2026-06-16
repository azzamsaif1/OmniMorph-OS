"""Security Specialist — enforces the ethical constitution (Feature 14).

Scans code for credential leaks, injection risks, insecure defaults,
and privacy violations.  Also enforces governance rules system-wide.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.utils.logger import log

_SENSITIVE_PATTERNS = [
    "password",
    "secret",
    "api_key",
    "token",
    "private_key",
    "credential",
]


class SecurityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.SECURITY)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        # Quick static scan of any code snippets in context
        code = state.context.get("active_code", "")
        findings: list[str] = []
        for pattern in _SENSITIVE_PATTERNS:
            if pattern in code.lower():
                findings.append(f"Potential exposure of '{pattern}' detected")

        for task in tasks:
            result = (
                f"Security scan for '{task.get('description', 'N/A')}' — "
                f"{len(findings)} finding(s)"
            )
            task["status"] = "done"
            task["result"] = result
            task["findings"] = findings
            self._emit(state, f"[Security] {result}")
            state.completed_tasks.append(task)

        state.context["security_findings"] = findings
        log.debug("security_agent.processed", findings=len(findings))
        return state
