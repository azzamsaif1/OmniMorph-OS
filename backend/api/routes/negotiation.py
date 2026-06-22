"""Negotiation API routes — diplomacy, contracts, conflict resolution."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/negotiation", tags=["negotiation"])


class NegotiationStartRequest(BaseModel):
    parties: list[str]
    topic: str
    constraints: dict | None = None


class NegotiationRoundRequest(BaseModel):
    session_id: str
    proposals: dict[str, str]


class ConflictRequest(BaseModel):
    party_a: str
    position_a: str
    party_b: str
    position_b: str


class ContractRequest(BaseModel):
    contract_type: str = "saas_agreement"
    parties: list[str]
    terms: dict = {}


class ContractReviewRequest(BaseModel):
    contract_text: str


@router.post("/start")
async def start_negotiation(req: NegotiationStartRequest):
    """Initialize a new negotiation session."""
    from backend.agents.negotiation.diplomat_agent import DiplomatAgent
    agent = DiplomatAgent()
    return await agent.start_negotiation(req.parties, req.topic, req.constraints)


@router.post("/round")
async def negotiation_round(req: NegotiationRoundRequest):
    """Execute one round of negotiation."""
    from backend.agents.negotiation.diplomat_agent import DiplomatAgent
    agent = DiplomatAgent()
    return await agent.negotiate_round(req.session_id, req.proposals)


@router.post("/resolve")
async def resolve_conflict(req: ConflictRequest):
    """Resolve a conflict between two parties."""
    from backend.agents.negotiation.diplomat_agent import DiplomatAgent
    agent = DiplomatAgent()
    return await agent.resolve_conflict(
        req.party_a, req.position_a, req.party_b, req.position_b
    )


@router.post("/contract/draft")
async def draft_contract(req: ContractRequest):
    """Draft a contract from specifications."""
    from backend.agents.negotiation.contract_agent import ContractAgent
    agent = ContractAgent()
    return await agent.draft_contract(req.contract_type, req.parties, req.terms)


@router.post("/contract/review")
async def review_contract(req: ContractReviewRequest):
    """Review a contract for risks and issues."""
    from backend.agents.negotiation.contract_agent import ContractAgent
    agent = ContractAgent()
    return await agent.review_contract(req.contract_text)
