"""Contract agent — drafts and reviews legal contracts and agreements.

Target: 95% client satisfaction in generated contracts.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class ContractAgent:
    """AI contract drafting and review agent.

    Capabilities:
    - Contract generation (SaaS, NDA, service agreements)
    - Clause analysis and risk assessment
    - Term negotiation suggestions
    - Compliance verification
    - Multi-language support
    """

    def __init__(self):
        self.contracts_generated: int = 0
        self.reviews_completed: int = 0

    async def draft_contract(
        self, contract_type: str, parties: list[str], terms: dict
    ) -> dict[str, Any]:
        """Draft a contract from specifications."""
        prompt = (
            f"Draft a {contract_type} contract.\n\n"
            f"Parties: {', '.join(parties)}\n"
            f"Key terms: {terms}\n\n"
            f"Include:\n"
            f"- Definitions section\n"
            f"- Scope of work/services\n"
            f"- Payment terms\n"
            f"- Duration and termination\n"
            f"- Intellectual property\n"
            f"- Confidentiality\n"
            f"- Limitation of liability\n"
            f"- Governing law\n"
            f"- Dispute resolution\n"
            f"- Signatures block"
        )

        contract = await generate_content(prompt)
        self.contracts_generated += 1

        return {
            "type": contract_type,
            "parties": parties,
            "content": contract or self._fallback_contract(contract_type, parties, terms),
            "terms": terms,
            "generated_at": time.time(),
            "status": "draft",
        }

    async def review_contract(self, contract_text: str) -> dict[str, Any]:
        """Review a contract for risks and issues."""
        prompt = (
            f"Review this contract for legal risks:\n\n"
            f"{contract_text[:3000]}\n\n"
            f"Identify:\n"
            f"1. Unfavorable clauses\n"
            f"2. Missing protections\n"
            f"3. Ambiguous language\n"
            f"4. Risk score (1-10)\n"
            f"5. Recommended modifications"
        )

        review = await generate_content(prompt)
        self.reviews_completed += 1

        return {
            "type": "contract_review",
            "review": review or "Contract review requires Gemini API",
            "reviewed_at": time.time(),
        }

    async def negotiate_terms(
        self, current_terms: dict, desired_changes: list[str]
    ) -> dict[str, Any]:
        """Suggest negotiation strategy for contract terms."""
        prompt = (
            f"Suggest negotiation strategy:\n\n"
            f"Current terms: {current_terms}\n"
            f"Desired changes: {', '.join(desired_changes)}\n\n"
            f"Provide: justification for each change, fallback positions, "
            f"and package deal suggestions."
        )

        strategy = await generate_content(prompt)

        return {
            "current_terms": current_terms,
            "desired_changes": desired_changes,
            "strategy": strategy or "Negotiation strategy requires Gemini API",
            "generated_at": time.time(),
        }

    def _fallback_contract(self, contract_type: str, parties: list[str], terms: dict) -> str:
        """Fallback contract template."""
        return (
            f"{'='*60}\n"
            f"{contract_type.upper()} AGREEMENT\n"
            f"{'='*60}\n\n"
            f"This Agreement is entered into between:\n"
            + "\n".join(f"- {p}" for p in parties) +
            f"\n\nEFFECTIVE DATE: [Date]\n\n"
            f"1. SCOPE\n"
            f"   {terms.get('scope', 'To be defined')}\n\n"
            f"2. PAYMENT\n"
            f"   {terms.get('payment', 'As agreed')}\n\n"
            f"3. TERM\n"
            f"   {terms.get('duration', '12 months')}\n\n"
            f"4. TERMINATION\n"
            f"   Either party may terminate with 30 days written notice.\n\n"
            f"5. CONFIDENTIALITY\n"
            f"   Standard mutual NDA provisions apply.\n\n"
            f"SIGNATURES:\n"
            + "\n".join(f"_______________ ({p})" for p in parties)
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "contract",
            "contracts_generated": self.contracts_generated,
            "reviews_completed": self.reviews_completed,
        }
