"""Research API — arXiv paper discovery, GitHub trending, knowledge updates."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.research.arxiv_reader import ArxivReader
from backend.research.github_tracker import GitHubTracker
from backend.research.knowledge_updater import KnowledgeUpdater

router = APIRouter()

_arxiv = ArxivReader()
_github = GitHubTracker()
_updater = KnowledgeUpdater(arxiv_reader=_arxiv, github_tracker=_github)


class SearchRequest(BaseModel):
    query: str
    max_results: int = Field(default=10, ge=1, le=50)


class TrendingRequest(BaseModel):
    language: str = ""
    topic: str = ""
    min_stars: int = Field(default=100, ge=0)
    limit: int = Field(default=10, ge=1, le=30)


@router.post("/arxiv/search")
async def search_arxiv(req: SearchRequest) -> dict[str, Any]:
    papers = await _arxiv.search(req.query, max_results=req.max_results)
    return {
        "query": req.query,
        "results": [p.to_dict() for p in papers],
        "count": len(papers),
    }


@router.get("/arxiv/latest")
async def latest_papers(categories: str = "") -> dict[str, Any]:
    cats = categories.split(",") if categories else None
    papers = await _arxiv.fetch_latest(categories=cats)
    return {
        "results": [p.to_dict() for p in papers],
        "count": len(papers),
    }


@router.post("/github/trending")
async def search_trending(req: TrendingRequest) -> dict[str, Any]:
    repos = await _github.search_trending(
        language=req.language,
        topic=req.topic,
        min_stars=req.min_stars,
        limit=req.limit,
    )
    return {
        "results": [r.to_dict() for r in repos],
        "count": len(repos),
    }


@router.post("/knowledge/update")
async def run_knowledge_update(
    topics: list[str] | None = None,
    languages: list[str] | None = None,
) -> dict[str, Any]:
    update = await _updater.run_update(topics=topics, languages=languages)
    return update.to_dict()


@router.get("/knowledge/last")
async def get_last_update() -> dict[str, Any]:
    update = _updater.last_update
    if update:
        return update.to_dict()
    return {"status": "no_updates_yet"}
