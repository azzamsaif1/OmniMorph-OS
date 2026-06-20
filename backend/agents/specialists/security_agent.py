"""Security Specialist — enforces the ethical constitution (Feature 14).

Scans code for credential leaks, injection risks, insecure defaults,
and privacy violations. Also enforces governance rules system-wide.
Uses Gemini for deep vulnerability analysis.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_analyze_code
from backend.governance.constitution import Constitution
from backend.utils.logger import log

_SENSITIVE_PATTERNS = [
    "password",
    "secret",
    "api_key",
    "token",
    "private_key",
    "credential",
    "AWS_SECRET",
    "STRIPE_SECRET",
]

_INJECTION_PATTERNS = [
    "exec(",
    "eval(",
    "os.system(",
    "subprocess.call(",
    "__import__(",
    "pickle.loads(",
]

_constitution = Constitution()


class SecurityAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.SECURITY)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        code = state.context.get("active_code", "")
        all_findings: list[dict[str, str]] = []
        static_findings: list[dict[str, str]] = []

        if code:
            static_findings = self._static_scan(code)
            all_findings.extend(static_findings)

        for task in tasks:
            task_findings: list[dict[str, str]] = list(static_findings)
            task_code = task.get("code", code)
            if task_code:
                gemini_result = await gemini_analyze_code(
                    code=task_code,
                    task="security_review",
                    language=task.get("language", "python"),
                )
                for issue in gemini_result.get("issues", []):
                    finding = {
                        "severity": issue.get("severity", "medium"),
                        "message": issue.get("message", ""),
                        "source": "gemini",
                    }
                    task_findings.append(finding)
                    all_findings.append(finding)

            constitutional_check = _constitution.validate_action({
                "type": task.get("action_type", "code_gen"),
                "consent": state.context.get("user_consent", True),
                "scope": task.get("scope", "internal"),
            })
            if not constitutional_check.permitted:
                for v in constitutional_check.violations:
                    finding = {"severity": "critical", "message": v, "source": "constitution"}
                    task_findings.append(finding)
                    all_findings.append(finding)

            result = (
                f"Security scan for '{task.get('description', 'N/A')}' — "
                f"{len(task_findings)} finding(s)"
            )
            task["status"] = "done"
            task["result"] = result
            task["findings"] = task_findings
            self._emit(state, f"[Security] {result}")
            state.completed_tasks.append(task)

        state.context["security_findings"] = all_findings
        log.debug("security_agent.processed", findings=len(all_findings))
        return state

    def _static_scan(self, code: str) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            lower = line.lower()
            for pat in _SENSITIVE_PATTERNS:
                if pat.lower() in lower and "=" in line and "#" not in line[:line.index("=")]:
                    findings.append({
                        "severity": "high",
                        "message": f"Line {i}: Potential hardcoded {pat}",
                        "source": "static",
                    })
            for pat in _INJECTION_PATTERNS:
                if pat in line:
                    findings.append({
                        "severity": "high",
                        "message": f"Line {i}: Potential injection via {pat.rstrip('(')}",
                        "source": "static",
                    })
        return findings
