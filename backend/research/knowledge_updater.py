"""Knowledge Updater — Weekly Automated Knowledge Base Refresh.

Orchestrates arXiv paper discovery and GitHub trending analysis
to keep UCSK's knowledge libraries current. Runs as a scheduled
background task and pushes updates to the vector store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.research.arxiv_reader import ArxivReader, PaperSummary
from backend.research.github_tracker import GitHubTracker, TrendingRepo
from backend.utils.logger import log


@dataclass
class KnowledgeUpdate:
    """Represents a single knowledge update batch."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    papers: list[PaperSummary] = field(default_factory=list)
    repos: list[TrendingRepo] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "papers_count": len(self.papers),
            "repos_count": len(self.repos),
            "insights": self.insights,
            "papers": [p.to_dict() for p in self.papers[:5]],
            "repos": [r.to_dict() for r in self.repos[:5]],
        }


class KnowledgeUpdater:
    """Coordinates periodic knowledge base updates.

    In production, this would be triggered by a scheduler (e.g., Celery Beat
    or APScheduler). For now it exposes an async method that can be called
    on-demand or via an API endpoint.
    """

    def __init__(
        self,
        arxiv_reader: ArxivReader | None = None,
        github_tracker: GitHubTracker | None = None,
    ) -> None:
        self._arxiv = arxiv_reader or ArxivReader()
        self._github = github_tracker or GitHubTracker()
        self._history: list[KnowledgeUpdate] = []

    async def run_update(
        self,
        topics: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> KnowledgeUpdate:
        """Execute a knowledge update cycle.

        Args:
            topics: Research topics to query (default: general SE/AI).
            languages: Programming languages to track on GitHub.

        Returns:
            KnowledgeUpdate with discovered papers and repos.
        """
        topics = topics or ["software engineering", "large language models", "code generation"]
        languages = languages or ["python", "typescript", "rust"]

        log.info("knowledge_updater.starting", topics=topics, languages=languages)

        # Fetch papers
        papers: list[PaperSummary] = []
        for topic in topics:
            batch = await self._arxiv.search(topic, max_results=5)
            papers.extend(batch)

        # Fetch trending repos
        repos: list[TrendingRepo] = []
        for lang in languages:
            batch = await self._github.search_trending(language=lang, limit=5)
            repos.extend(batch)

        # Generate simple insights
        insights = self._generate_insights(papers, repos)

        update = KnowledgeUpdate(
            papers=papers,
            repos=repos,
            insights=insights,
        )
        self._history.append(update)
        log.info(
            "knowledge_updater.complete",
            papers=len(papers),
            repos=len(repos),
            insights=len(insights),
        )
        return update

    @property
    def last_update(self) -> KnowledgeUpdate | None:
        return self._history[-1] if self._history else None

    def _generate_insights(
        self, papers: list[PaperSummary], repos: list[TrendingRepo]
    ) -> list[str]:
        """Generate high-level insights from discovered content."""
        insights: list[str] = []
        if papers:
            top_cats = {}
            for p in papers:
                for c in p.categories:
                    top_cats[c] = top_cats.get(c, 0) + 1
            if top_cats:
                hottest = max(top_cats, key=top_cats.get)  # type: ignore[arg-type]
                insights.append(
                    f"Most active research area: {hottest} ({top_cats[hottest]} papers)"
                )
        if repos:
            top_lang = {}
            for r in repos:
                if r.language:
                    top_lang[r.language] = top_lang.get(r.language, 0) + r.stars
            if top_lang:
                hottest_lang = max(top_lang, key=top_lang.get)  # type: ignore[arg-type]
                insights.append(
                    f"Trending language by stars: {hottest_lang} ({top_lang[hottest_lang]:,} total stars)"
                )
        return insights
