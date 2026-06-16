"""arXiv Reader — Automated Research Paper Discovery.

Queries the arXiv API for papers relevant to the user's skill domains.
Extracts abstracts, key techniques, and actionable insights.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from backend.utils.logger import log

_ARXIV_API = "http://export.arxiv.org/api/query"

# Default categories relevant to software engineering
_DEFAULT_CATEGORIES = [
    "cs.SE",  # Software Engineering
    "cs.AI",  # Artificial Intelligence
    "cs.PL",  # Programming Languages
    "cs.DC",  # Distributed Computing
    "cs.CR",  # Cryptography & Security
]


@dataclass
class PaperSummary:
    """Condensed representation of an arXiv paper."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: datetime
    url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors[:3],  # first 3 authors
            "abstract_snippet": self.abstract[:300],
            "categories": self.categories,
            "published": self.published.isoformat(),
            "url": self.url,
        }


class ArxivReader:
    """Fetches and parses papers from arXiv's Atom API."""

    def __init__(
        self,
        categories: list[str] | None = None,
        max_results: int = 10,
    ) -> None:
        self._categories = categories or _DEFAULT_CATEGORIES
        self._max_results = max_results

    async def search(
        self, query: str, max_results: int | None = None
    ) -> list[PaperSummary]:
        """Search arXiv for papers matching a query.

        Args:
            query: Free-text search query.
            max_results: Override default result count.

        Returns:
            List of PaperSummary objects.
        """
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results or self._max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(_ARXIV_API, params=params)
                resp.raise_for_status()
                return self._parse_atom_feed(resp.text)
        except httpx.HTTPError as exc:
            log.warning("arxiv.search_failed", error=str(exc))
            return []

    async def fetch_latest(
        self, categories: list[str] | None = None
    ) -> list[PaperSummary]:
        """Fetch the latest papers from configured categories."""
        cats = categories or self._categories
        cat_query = " OR ".join(f"cat:{c}" for c in cats)
        return await self.search(cat_query)

    def _parse_atom_feed(self, xml_text: str) -> list[PaperSummary]:
        """Minimal XML parsing for arXiv Atom feed."""
        import xml.etree.ElementTree as ET

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_text)
        papers: list[PaperSummary] = []

        for entry in root.findall("atom:entry", ns):
            arxiv_id = (entry.findtext("atom:id", "", ns) or "").split("/abs/")[-1]
            title = (entry.findtext("atom:title", "", ns) or "").strip().replace("\n", " ")
            abstract = (entry.findtext("atom:summary", "", ns) or "").strip().replace("\n", " ")
            authors = [
                a.findtext("atom:name", "", ns) or ""
                for a in entry.findall("atom:author", ns)
            ]
            published_str = entry.findtext("atom:published", "", ns) or ""
            categories = [
                c.get("term", "")
                for c in entry.findall("atom:category", ns)
                if c.get("term")
            ]
            link = ""
            for lnk in entry.findall("atom:link", ns):
                if lnk.get("type") == "text/html":
                    link = lnk.get("href", "")
                    break
            if not link:
                link = f"https://arxiv.org/abs/{arxiv_id}"

            try:
                published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except ValueError:
                published = datetime.now(timezone.utc)

            papers.append(
                PaperSummary(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    categories=categories,
                    published=published,
                    url=link,
                )
            )
        return papers
