"""Sales agent — automated outreach, lead scoring, and proposal generation."""

import time
from typing import Any

from backend.gemini_client import generate_content


class SalesAgent:
    """Automated sales agent for lead management and outreach.

    Capabilities:
    - Lead scoring and qualification
    - Outreach email generation
    - Proposal/pitch deck content
    - Follow-up scheduling
    - Pipeline management
    """

    def __init__(self):
        self.leads_processed: int = 0
        self.proposals_generated: int = 0

    async def score_lead(self, lead_data: dict) -> dict[str, Any]:
        """Score and qualify a lead based on available data."""
        company = lead_data.get("company", "Unknown")
        industry = lead_data.get("industry", "Technology")
        size = lead_data.get("company_size", "unknown")
        budget = lead_data.get("estimated_budget", "unknown")

        prompt = (
            f"Score this lead (1-100) and provide qualification assessment:\n\n"
            f"Company: {company}\nIndustry: {industry}\n"
            f"Size: {size}\nBudget: {budget}\n\n"
            f"Our product: AI-native cognitive operating system for education/productivity.\n"
            f"Scoring criteria: fit, budget, urgency, authority, need."
        )

        response = await generate_content(prompt)
        self.leads_processed += 1

        # Extract score from response
        score = 50  # default
        if response:
            for word in response.split():
                try:
                    num = int(word.strip(".,;:/()"))
                    if 1 <= num <= 100:
                        score = num
                        break
                except ValueError:
                    continue

        return {
            "lead": lead_data,
            "score": score,
            "qualified": score >= 60,
            "tier": "A" if score >= 80 else "B" if score >= 60 else "C",
            "reasoning": response or "Scoring requires Gemini API",
            "scored_at": time.time(),
        }

    async def generate_outreach(
        self, lead_data: dict, tone: str = "professional"
    ) -> dict[str, Any]:
        """Generate personalized outreach email."""
        company = lead_data.get("company", "your company")
        contact = lead_data.get("contact_name", "there")
        pain_point = lead_data.get("pain_point", "productivity optimization")

        prompt = (
            f"Write a {tone} cold outreach email:\n\n"
            f"To: {contact} at {company}\n"
            f"Pain point: {pain_point}\n"
            f"Our solution: UCSK — AI-native cognitive OS that adapts to mental state\n\n"
            f"Requirements: personalized, concise (< 150 words), clear CTA, no spam words."
        )

        email = await generate_content(prompt)

        return {
            "type": "outreach_email",
            "to": lead_data,
            "content": email or self._fallback_email(contact, company),
            "tone": tone,
            "generated_at": time.time(),
        }

    async def generate_proposal(
        self, client_needs: str, tier: str = "pro"
    ) -> dict[str, Any]:
        """Generate sales proposal content."""
        prompt = (
            f"Generate a sales proposal outline for:\n\n"
            f"Client needs: {client_needs}\n"
            f"Proposed tier: {tier}\n"
            f"Product: UCSK — cognitive operating system with 13 AI agents\n\n"
            f"Include: executive summary, proposed solution, pricing, timeline, ROI estimate."
        )

        proposal = await generate_content(prompt)
        self.proposals_generated += 1

        return {
            "type": "proposal",
            "client_needs": client_needs,
            "tier": tier,
            "content": proposal or "Proposal generation requires Gemini API",
            "generated_at": time.time(),
        }

    def _fallback_email(self, contact: str, company: str) -> str:
        return (
            f"Hi {contact},\n\n"
            f"I noticed {company} is scaling its engineering team. "
            f"Our AI-native platform adapts in real-time to how your developers work — "
            f"reducing cognitive load and boosting flow state by 40%.\n\n"
            f"Would you be open to a 15-minute demo this week?\n\n"
            f"Best regards"
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "agent": "sales",
            "leads_processed": self.leads_processed,
            "proposals_generated": self.proposals_generated,
        }
