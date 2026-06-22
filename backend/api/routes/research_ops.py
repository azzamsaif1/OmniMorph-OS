"""Research operations API routes — arXiv scanning, knowledge extraction, self-evolution."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/research-ops", tags=["research"])


class ScanRequest(BaseModel):
    query: str = "AI agents"
    max_results: int = 100
    days_back: int = 7


class ExtractRequest(BaseModel):
    title: str
    abstract: str
    categories: list[str] = ["cs.AI"]


class EvolveRequest(BaseModel):
    knowledge_items: list[dict] = []


@router.post("/scan")
async def scan_arxiv(req: ScanRequest):
    """Scan arXiv for recent papers matching query."""
    from backend.agents.research.arxiv_scanner import ArxivScanner
    scanner = ArxivScanner()
    papers = await scanner.scan_recent_papers(req.query, req.max_results, req.days_back)
    return {"papers": papers, "count": len(papers), "stats": scanner.get_scan_stats()}


@router.post("/extract")
async def extract_knowledge(req: ExtractRequest):
    """Extract structured knowledge from a paper."""
    from backend.agents.research.knowledge_extractor import KnowledgeExtractor
    extractor = KnowledgeExtractor()
    paper = {"title": req.title, "abstract": req.abstract, "categories": req.categories}
    knowledge = await extractor.extract_from_paper(paper)
    return knowledge


@router.post("/evolve")
async def self_evolve(req: EvolveRequest):
    """Execute one self-evolution cycle (MUSE-style)."""
    from backend.agents.research.self_evolver import SelfEvolver
    evolver = SelfEvolver()
    result = await evolver.evolve(req.knowledge_items)
    return result


@router.get("/stats")
async def research_stats():
    """Get research agent statistics."""
    from backend.agents.research.arxiv_scanner import ArxivScanner
    from backend.agents.research.self_evolver import SelfEvolver
    scanner = ArxivScanner()
    evolver = SelfEvolver()
    return {
        "scanner": scanner.get_scan_stats(),
        "evolver": evolver.get_evolution_stats(),
    }
