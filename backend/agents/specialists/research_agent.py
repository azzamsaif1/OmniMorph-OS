"""Research Specialist — autonomous scientific intelligence (Feature 6).

Monitors arXiv, GitHub trending, and documentation sources to surface
relevant papers, libraries, and patterns for the user's current work.
"""

from __future__ import annotations

from backend.agents.base import AgentRole, AgentState, BaseAgent
from backend.research.arxiv_reader import ArxivReader
from backend.research.github_tracker import GitHubTracker
from backend.utils.logger import log


class ResearchAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentRole.RESEARCH)
        self._arxiv = ArxivReader(max_results=5)
        self._github = GitHubTracker()

    async def process(self, state: AgentState) -> AgentState:
        tasks = [
            t
            for t in state.context.get("dispatched_tasks", [])
            if t.get("assigned_to") == self.role.value
        ]

        work = state.context.get("work_context", {})
        language = work.get("current_language", "python")
        framework = work.get("framework", "")

        for task in tasks:
            topic = task.get("topic", framework or language)
            recommendations: list[dict[str, str]] = []

            try:
                papers = await self._arxiv.search(topic, max_results=3)
                for p in papers:
                    recommendations.append({
                        "type": "paper",
                        "title": p.title,
                        "url": p.url,
                        "summary": p.abstract[:200],
                    })
            except Exception as exc:
                log.warning("research_agent.arxiv_error", error=str(exc))

            try:
                repos = await self._github.search_trending(
                    language=language, min_stars=50, limit=3
                )
                for r in repos:
                    recommendations.append({
                        "type": "repo",
                        "title": r.full_name,
                        "url": r.url,
                        "summary": r.description[:200],
                        "stars": str(r.stars),
                    })
            except Exception as exc:
                log.warning("research_agent.github_error", error=str(exc))

            task["status"] = "done"
            task["result"] = recommendations
            self._emit(
                state,
                f"[Research] Found {len(recommendations)} recommendations for '{topic}'",
            )
            state.completed_tasks.append(task)

        log.debug("research_agent.processed", tasks=len(tasks))
        return state
