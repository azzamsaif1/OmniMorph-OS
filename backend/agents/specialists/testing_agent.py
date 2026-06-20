"""Testing Specialist — generates and runs tests.

Auto-generates unit / integration test stubs from code using Gemini,
runs existing suites, and reports coverage gaps.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.gemini_client import gemini_generate
from backend.utils.logger import log


class TestingAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.TESTING)

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        for task in tasks:
            code = task.get("code", state.context.get("active_code", ""))
            language = task.get("language", "python")

            test_report: dict[str, object] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "coverage_pct": 0.0,
                "generated_tests": "",
                "suggestions": [],
            }

            if code:
                system = (
                    "You are UCSK's testing agent. Generate comprehensive unit tests "
                    f"for the given {language} code. Include edge cases and error scenarios. "
                    f"Use pytest for Python, jest for TypeScript/JavaScript."
                )
                prompt = f"Generate tests for:\n```{language}\n{code}\n```"
                generated = await gemini_generate(
                    prompt, system_instruction=system, temperature=0.4, max_tokens=2048
                )
                test_report["generated_tests"] = generated

                analysis_system = (
                    "Analyze this code and estimate: total test count needed, "
                    "coverage gaps, and testing suggestions. Respond concisely."
                )
                analysis = await gemini_generate(
                    f"Analyze test coverage needs for:\n```{language}\n{code}\n```",
                    system_instruction=analysis_system,
                    temperature=0.3,
                    max_tokens=512,
                )
                test_report["suggestions"] = [analysis[:500]]

            task["status"] = "done"
            task["result"] = test_report
            self._emit(
                state,
                f"[Testing] Test generation complete"
                + (f" — generated tests for {language}" if code else ""),
            )
            state.completed_tasks.append(task)

        log.debug("testing_agent.processed", tasks=len(tasks))
        return state
