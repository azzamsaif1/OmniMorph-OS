"""Mixture of Experts (MoE) router — routes queries to specialized models.

In the nucleus, uses MoE to route queries to the specialized model
that is best suited to handle them.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class MoERouter:
    """Routes incoming queries to the most appropriate specialist model.

    Expert domains:
    - security: vulnerability analysis, penetration testing
    - trading: market analysis, signal generation
    - software: code generation, review, testing
    - research: paper analysis, knowledge extraction
    - business: market analysis, sales
    - negotiation: conflict resolution, contracts
    - delivery: project planning, deployment
    """

    EXPERTS = {
        "security": {
            "keywords": ["vulnerability", "exploit", "cve", "security", "penetration",
                        "attack", "firewall", "encryption", "authentication", "breach"],
            "description": "Security and penetration testing",
            "confidence_threshold": 0.7,
        },
        "trading": {
            "keywords": ["trading", "stock", "portfolio", "market", "investment",
                        "price", "indicator", "rsi", "macd", "financial"],
            "description": "Financial trading and analysis",
            "confidence_threshold": 0.7,
        },
        "software": {
            "keywords": ["code", "function", "class", "api", "database", "frontend",
                        "backend", "test", "deploy", "refactor", "bug"],
            "description": "Software engineering",
            "confidence_threshold": 0.6,
        },
        "research": {
            "keywords": ["paper", "research", "arxiv", "study", "methodology",
                        "hypothesis", "experiment", "novel", "literature"],
            "description": "Research and knowledge extraction",
            "confidence_threshold": 0.7,
        },
        "business": {
            "keywords": ["market", "competitor", "revenue", "customer", "lead",
                        "sales", "pricing", "strategy", "growth"],
            "description": "Business analysis and sales",
            "confidence_threshold": 0.6,
        },
        "negotiation": {
            "keywords": ["negotiate", "contract", "agreement", "terms", "proposal",
                        "consensus", "conflict", "resolution", "parties"],
            "description": "Negotiation and contract management",
            "confidence_threshold": 0.7,
        },
        "delivery": {
            "keywords": ["project", "plan", "sprint", "deploy", "docker",
                        "pipeline", "ci", "cd", "release", "version"],
            "description": "Project delivery and deployment",
            "confidence_threshold": 0.6,
        },
    }

    def __init__(self):
        self.routing_history: list[dict] = []
        self.expert_usage: dict[str, int] = {k: 0 for k in self.EXPERTS}

    def route(self, query: str) -> dict[str, Any]:
        """Route a query to the best expert.

        Uses keyword matching + confidence scoring.
        Falls back to 'software' as default expert.
        """
        query_lower = query.lower()
        scores: dict[str, float] = {}

        for expert_name, expert_config in self.EXPERTS.items():
            keywords = expert_config["keywords"]
            matches = sum(1 for kw in keywords if kw in query_lower)
            score = matches / len(keywords) if keywords else 0.0
            scores[expert_name] = score

        # Find best match
        best_expert = max(scores, key=scores.get)  # type: ignore
        best_score = scores[best_expert]
        threshold = self.EXPERTS[best_expert]["confidence_threshold"]

        # If no clear winner, use AI to decide
        if best_score < 0.1:
            best_expert = "software"  # Default
            best_score = 0.5

        routed = best_score >= threshold * 0.5  # Relaxed threshold for routing

        result = {
            "query": query[:100],
            "routed_to": best_expert,
            "confidence": best_score,
            "all_scores": scores,
            "routed": routed,
            "fallback": not routed,
            "timestamp": time.time(),
        }

        self.routing_history.append(result)
        self.expert_usage[best_expert] = self.expert_usage.get(best_expert, 0) + 1

        return result

    async def route_with_ai(self, query: str) -> dict[str, Any]:
        """Use Gemini to intelligently route complex queries."""
        # First try keyword routing
        basic_route = self.route(query)

        # If confidence is low, use AI
        if basic_route["confidence"] < 0.3:
            experts_desc = "\n".join(
                f"- {name}: {config['description']}"
                for name, config in self.EXPERTS.items()
            )

            prompt = (
                f"Route this query to the most appropriate expert:\n\n"
                f"Query: {query}\n\n"
                f"Available experts:\n{experts_desc}\n\n"
                f"Respond with just the expert name (one word)."
            )

            response = await generate_content(prompt)

            if response:
                for expert_name in self.EXPERTS:
                    if expert_name in response.lower():
                        basic_route["routed_to"] = expert_name
                        basic_route["confidence"] = 0.8
                        basic_route["ai_routed"] = True
                        break

        return basic_route

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics."""
        total = len(self.routing_history)
        avg_confidence = (
            sum(r["confidence"] for r in self.routing_history) / total
            if total > 0 else 0.0
        )

        return {
            "total_queries_routed": total,
            "expert_usage": self.expert_usage,
            "avg_confidence": avg_confidence,
            "fallback_rate": (
                sum(1 for r in self.routing_history if r.get("fallback", False)) / max(total, 1)
            ),
        }
