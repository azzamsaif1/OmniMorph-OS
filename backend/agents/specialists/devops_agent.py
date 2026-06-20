"""DevOps Specialist — CI/CD, deployment, and infrastructure tasks.

Manages container builds, deployment pipelines, monitoring config,
and infrastructure-as-code resources. Uses Gemini for advice.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_generate
from backend.utils.logger import log


class DevOpsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.DEVOPS)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        for task in tasks:
            desc = task.get("description", "deploy")
            code = task.get("code", "")

            report: dict[str, object] = {
                "action": desc,
                "status": "completed",
                "recommendations": [],
            }

            if code or desc:
                system = (
                    "You are UCSK's DevOps agent. Analyze the infrastructure/deployment "
                    "configuration and suggest improvements for: reliability, scalability, "
                    "security, cost optimization, and CI/CD pipeline efficiency. Be concise."
                )
                content = code if code else f"Task: {desc}"
                advice = await gemini_generate(
                    f"Analyze DevOps configuration:\n{content[:2000]}",
                    system_instruction=system,
                    temperature=0.4,
                    max_tokens=512,
                )
                report["recommendations"] = [advice[:500]]

            task["status"] = "done"
            task["result"] = report
            self._emit(
                state,
                f"[DevOps] '{desc}' — {report['status']}",
            )
            state.completed_tasks.append(task)

        log.debug("devops_agent.processed", tasks=len(tasks))
        return state
