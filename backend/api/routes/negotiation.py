"""Negotiation API routes — diplomacy, contracts, conflict resolution."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.negotiation.diplomat_agent import DiplomatAgent
from backend.agents.negotiation.contract_agent import ContractAgent

router = APIRouter(prefix="/api/negotiation", tags=["negotiation"])

# Module-level singletons so session state persists across requests
_diplomat = DiplomatAgent()
_contract = ContractAgent()


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
    return await _diplomat.start_negotiation(req.parties, req.topic, req.constraints)


@router.post("/round")
async def negotiation_round(req: NegotiationRoundRequest):
    """Execute one round of negotiation."""
    return await _diplomat.negotiate_round(req.session_id, req.proposals)


@router.post("/resolve")
async def resolve_conflict(req: ConflictRequest):
    """Resolve a conflict between two parties."""
    return await _diplomat.resolve_conflict(
        req.party_a, req.position_a, req.party_b, req.position_b
    )


@router.post("/contract/draft")
async def draft_contract(req: ContractRequest):
    """Draft a contract from specifications."""
    return await _contract.draft_contract(req.contract_type, req.parties, req.terms)


@router.post("/contract/review")
async def review_contract(req: ContractReviewRequest):
    """Review a contract for risks and issues."""
    return await _contract.review_contract(req.contract_text)
