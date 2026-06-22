"""Planner agent — requirements analysis, task decomposition, scheduling.

Target: 90% accuracy in requirements analysis.
Source: CrewAI (95% automation)
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class PlannerAgent:
    """Project planning agent — decomposes projects into executable tasks.

    Capabilities:
    - Requirements analysis and decomposition
    - Task dependency mapping
    - Effort estimation
    - Sprint planning
    - Risk identification
    """

    def __init__(self):
        self.plans_created: int = 0

    async def analyze_requirements(self, project_description: str) -> dict[str, Any]:
        """Analyze project requirements and decompose into tasks."""
        prompt = (
            f"Analyze this project and create a detailed plan:\n\n"
            f"{project_description}\n\n"
            f"Provide:\n"
            f"1. Functional requirements (numbered list)\n"
            f"2. Non-functional requirements\n"
            f"3. Task breakdown (with estimates in hours)\n"
            f"4. Dependencies between tasks\n"
            f"5. Risk assessment\n"
            f"6. Suggested timeline (in sprints)"
        )

        analysis = await generate_content(prompt)
        self.plans_created += 1

        return {
            "type": "requirements_analysis",
            "project": project_description[:100],
            "analysis": analysis or self._fallback_plan(project_description),
            "created_at": time.time(),
        }

    async def create_sprint_plan(
        self, tasks: list[str], sprint_duration_days: int = 14, team_size: int = 3
    ) -> dict[str, Any]:
        """Create a sprint plan from task list."""
        prompt = (
            f"Create a sprint plan:\n\n"
            f"Tasks: {', '.join(tasks)}\n"
            f"Sprint duration: {sprint_duration_days} days\n"
            f"Team size: {team_size}\n\n"
            f"Assign tasks, set priorities, identify blockers."
        )

        plan = await generate_content(prompt)

        return {
            "type": "sprint_plan",
            "tasks": tasks,
            "duration_days": sprint_duration_days,
            "team_size": team_size,
            "plan": plan or "Sprint planning requires Gemini API",
            "created_at": time.time(),
        }

    async def estimate_effort(self, task_description: str) -> dict[str, Any]:
        """Estimate effort for a task in hours."""
        prompt = (
            f"Estimate effort for: {task_description}\n\n"
            f"Provide: optimistic, most likely, and pessimistic estimates (hours).\n"
            f"Use three-point estimation (PERT): E = (O + 4M + P) / 6"
        )

        response = await generate_content(prompt)

        return {
            "task": task_description,
            "estimate": response or "4-8 hours (default estimate)",
            "estimated_at": time.time(),
        }

    def _fallback_plan(self, description: str) -> str:
        return (
            f"Project Plan for: {description[:50]}...\n\n"
            f"Phase 1 (Sprint 1-2): Foundation\n"
            f"  - Architecture design (8h)\n"
            f"  - Core implementation (16h)\n"
            f"  - Database schema (4h)\n\n"
            f"Phase 2 (Sprint 3-4): Features\n"
            f"  - API endpoints (12h)\n"
            f"  - Frontend UI (16h)\n"
            f"  - Integration (8h)\n\n"
            f"Phase 3 (Sprint 5): Polish\n"
            f"  - Testing (8h)\n"
            f"  - Documentation (4h)\n"
            f"  - Deployment (4h)\n"
        )

    def get_stats(self) -> dict[str, Any]:
        return {"agent": "planner", "plans_created": self.plans_created}
