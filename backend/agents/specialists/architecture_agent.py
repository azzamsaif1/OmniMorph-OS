"""Architecture Specialist — evaluates system design decisions.

Analyses module dependencies, coupling metrics, and design patterns.
Suggests architectural improvements and flags anti-patterns using Gemini.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_generate
from backend.utils.logger import log


class ArchitectureAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.ARCHITECTURE)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        for task in tasks:
            code = task.get("code", state.context.get("active_code", ""))
            desc = task.get("description", "")

            review: dict[str, object] = {
                "coupling_score": 0.0,
                "cohesion_score": 0.0,
                "patterns_detected": [],
                "suggestions": [],
            }

            if code:
                imports = [
                    line.strip()
                    for line in code.split("\n")
                    if line.strip().startswith(("import ", "from "))
                ]
                review["coupling_score"] = min(len(imports) / 15.0, 1.0)

                classes = [
                    line.strip()
                    for line in code.split("\n")
                    if line.strip().startswith("class ")
                ]
                functions = [
                    line.strip()
                    for line in code.split("\n")
                    if line.strip().startswith("def ") or line.strip().startswith("async def ")
                ]
                review["cohesion_score"] = min(
                    len(functions) / max(len(classes) * 5, 1), 1.0
                )

                system = (
                    "You are UCSK's architecture agent. Analyze the code structure and provide: "
                    "1) Design patterns detected, 2) Coupling/cohesion assessment, "
                    "3) Architectural suggestions. Be concise (3-5 bullet points)."
                )
                analysis = await gemini_generate(
                    f"Analyze architecture of:\n```python\n{code[:3000]}\n```\nContext: {desc}",
                    system_instruction=system,
                    temperature=0.4,
                    max_tokens=512,
                )
                review["suggestions"] = [analysis[:800]]
            else:
                review["suggestions"] = [
                    "Consider extracting shared types into a common module",
                ]

            task["status"] = "done"
            task["result"] = review
            self._emit(
                state,
                f"[Architecture] Review complete — coupling={review['coupling_score']:.2f} "
                f"cohesion={review['cohesion_score']:.2f}",
            )
            state.completed_tasks.append(task)

        log.debug("architecture_agent.processed", tasks=len(tasks))
        return state
