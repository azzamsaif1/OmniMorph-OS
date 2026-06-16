"""GitHub Tracker — Trending Repository & Technology Analysis.

Monitors GitHub trending repositories to identify emerging tools,
frameworks, and techniques relevant to the user's skill profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.utils.logger import log

_GITHUB_API = "https://api.github.com"


@dataclass
class TrendingRepo:
    """Summary of a trending GitHub repository."""

    full_name: str
    description: str
    language: str | None
    stars: int
    forks: int
    topics: list[str]
    url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "full_name": self.full_name,
            "description": self.description[:200] if self.description else "",
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
            "topics": self.topics[:5],
            "url": self.url,
        }


class GitHubTracker:
    """Tracks trending repositories and technology shifts on GitHub."""

    def __init__(self, token: str = "") -> None:
        self._token = token
        self._headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    async def search_trending(
        self,
        language: str = "",
        topic: str = "",
        min_stars: int = 100,
        limit: int = 10,
    ) -> list[TrendingRepo]:
        """Search GitHub for trending repositories.

        Args:
            language: Filter by programming language.
            topic: Filter by topic/tag.
            min_stars: Minimum star count.
            limit: Max results to return.

        Returns:
            List of TrendingRepo objects sorted by stars descending.
        """
        query_parts = [f"stars:>={min_stars}"]
        if language:
            query_parts.append(f"language:{language}")
        if topic:
            query_parts.append(f"topic:{topic}")

        params = {
            "q": " ".join(query_parts),
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 30),
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{_GITHUB_API}/search/repositories",
                    params=params,
                    headers=self._headers,
                )
                resp.raise_for_status()
                data = resp.json()
                return self._parse_results(data.get("items", []))
        except httpx.HTTPError as exc:
            log.warning("github.search_failed", error=str(exc))
            return []

    async def get_repo_topics(self, owner: str, repo: str) -> list[str]:
        """Fetch topics for a specific repository."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{_GITHUB_API}/repos/{owner}/{repo}/topics",
                    headers=self._headers,
                )
                resp.raise_for_status()
                return resp.json().get("names", [])
        except httpx.HTTPError:
            return []

    def _parse_results(self, items: list[dict[str, Any]]) -> list[TrendingRepo]:
        repos: list[TrendingRepo] = []
        for item in items:
            repos.append(
                TrendingRepo(
                    full_name=item.get("full_name", ""),
                    description=item.get("description", "") or "",
                    language=item.get("language"),
                    stars=item.get("stargazers_count", 0),
                    forks=item.get("forks_count", 0),
                    topics=item.get("topics", []),
                    url=item.get("html_url", ""),
                )
            )
        return repos
