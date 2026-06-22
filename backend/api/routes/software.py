"""Software engineering API routes — code generation, review, testing."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/software", tags=["software"])


class CodeGenRequest(BaseModel):
    description: str
    type: str = "web"  # web|systems|ai|devops|database|frontend
    language: str = "python"
    framework: str = "react"


class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    focus: str = "general"  # general|security|performance


class SecurityReviewRequest(BaseModel):
    code: str
    language: str = "python"


@router.post("/generate")
async def generate_code(req: CodeGenRequest):
    """Generate code using the software engineering orchestrator (8 agents)."""
    from backend.agents.software.software_orchestrator import SoftwareOrchestrator
    orchestrator = SoftwareOrchestrator()
    return await orchestrator.execute_task({
        "description": req.description,
        "type": req.type,
        "language": req.language,
    })


@router.post("/review")
async def review_code(req: CodeReviewRequest):
    """AI-powered code review."""
    from backend.agents.software.code_review_agent import CodeReviewAgent
    agent = CodeReviewAgent()
    return await agent.review(req.code, req.language, req.focus)


@router.post("/security-review")
async def security_review(req: SecurityReviewRequest):
    """Security-focused code review (OWASP Top 10)."""
    from backend.agents.software.security_code_agent import SecurityCodeAgent
    agent = SecurityCodeAgent()
    return await agent.review_code(req.code, req.language)


@router.get("/stats")
async def get_stats():
    """Get software agent performance statistics."""
    from backend.agents.software.software_orchestrator import SoftwareOrchestrator
    orchestrator = SoftwareOrchestrator()
    return orchestrator.get_all_stats()
