"""Software engineering orchestrator — coordinates 8 specialist agents.

Workflow: Planning → Coding → Review → Testing (from Agyn architecture).
"""

import time
from typing import Any

from backend.agents.software.web_agent import WebAgent
from backend.agents.software.systems_agent import SystemsAgent
from backend.agents.software.security_code_agent import SecurityCodeAgent
from backend.agents.software.ai_agent import AIAgent
from backend.agents.software.devops_sw_agent import DevOpsSWAgent
from backend.agents.software.testing_sw_agent import TestingSWAgent
from backend.agents.software.database_agent import DatabaseAgent
from backend.agents.software.frontend_agent import FrontendAgent
from backend.agents.software.code_review_agent import CodeReviewAgent


class SoftwareOrchestrator:
    """Orchestrates the full software development lifecycle with 8 agents.

    Pipeline: Plan → Route to specialist → Generate → Review → Test → Deliver
    """

    def __init__(self):
        self.web = WebAgent()
        self.systems = SystemsAgent()
        self.security = SecurityCodeAgent()
        self.ai = AIAgent()
        self.devops = DevOpsSWAgent()
        self.testing = TestingSWAgent()
        self.database = DatabaseAgent()
        self.frontend = FrontendAgent()
        self.code_review = CodeReviewAgent()

        self.task_history: list[dict] = []

    async def execute_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Route and execute a software engineering task.

        Task should contain:
        - description: what to build
        - type: web|systems|ai|devops|database|frontend
        - language: programming language
        """
        task_type = task.get("type", "web")
        description = task.get("description", "")
        language = task.get("language", "python")

        start_time = time.time()

        # Phase 1: Route to appropriate agent
        agent = self._route_task(task_type)

        # Phase 2: Generate code
        if task_type == "web":
            result = await self.web.generate_component(description)
        elif task_type == "systems":
            result = await self.systems.generate_c_code(description)
        elif task_type == "ai":
            result = await self.ai.design_model(description)
        elif task_type == "devops":
            result = await self.devops.generate_dockerfile(description, language)
        elif task_type == "database":
            entities = task.get("entities", [description])
            result = await self.database.design_schema(entities)
        elif task_type == "frontend":
            result = await self.frontend.design_page(description)
        else:
            result = await self.web.generate_component(description)

        # Phase 3: Security review
        code = result.get("code", "")
        if code and len(code) > 50:
            security_review = await self.security.review_code(code, language)
            result["security_review"] = security_review

        # Phase 4: Code review
        if code and len(code) > 50:
            review = await self.code_review.review(code, language)
            result["code_review"] = review

        # Phase 5: Generate tests
        if code and len(code) > 50:
            tests = await self.testing.generate_unit_tests(code, language)
            result["tests"] = tests

        result["execution_time"] = time.time() - start_time
        result["pipeline"] = ["plan", "generate", "security_review", "code_review", "test"]

        self.task_history.append({
            "task": task,
            "result_type": result.get("type"),
            "execution_time": result["execution_time"],
            "timestamp": time.time(),
        })

        return result

    def _route_task(self, task_type: str) -> str:
        """Route task to the appropriate specialist agent."""
        routing = {
            "web": "web",
            "api": "web",
            "systems": "systems",
            "c": "systems",
            "kernel": "systems",
            "ai": "ai",
            "ml": "ai",
            "devops": "devops",
            "docker": "devops",
            "k8s": "devops",
            "database": "database",
            "sql": "database",
            "frontend": "frontend",
            "ui": "frontend",
        }
        return routing.get(task_type, "web")

    def get_all_stats(self) -> dict[str, Any]:
        """Get performance stats from all agents."""
        return {
            "total_tasks": len(self.task_history),
            "agents": {
                "web": self.web.get_stats(),
                "systems": self.systems.get_stats(),
                "security": self.security.get_stats(),
                "ai": self.ai.get_stats(),
                "devops": self.devops.get_stats(),
                "testing": self.testing.get_stats(),
                "database": self.database.get_stats(),
                "frontend": self.frontend.get_stats(),
                "code_review": self.code_review.get_stats(),
            },
        }
