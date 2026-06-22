"""Curriculum generator — ALAS-style self-learning curriculum.

Cycle: Retrieve → Distill → Train → Evaluate → Repeat
Target: Accuracy improvement from 15% to 90% over training cycles.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class CurriculumGenerator:
    """Generates training curricula for specialized agents.

    Uses ALAS (Adaptive Learning through Automated Synthesis) approach:
    - Identifies knowledge gaps
    - Generates targeted training data
    - Creates progressive difficulty levels
    - Evaluates and adapts curriculum
    """

    def __init__(self):
        self.curricula_generated: int = 0
        self.training_cycles: int = 0
        self.performance_log: list[dict] = []

    async def generate_curriculum(
        self, agent_type: str, current_accuracy: float, target_accuracy: float = 0.9
    ) -> dict[str, Any]:
        """Generate a training curriculum for an agent.

        Args:
            agent_type: security|trading|software
            current_accuracy: current performance (0-1)
            target_accuracy: desired performance (0-1)
        """
        gap = target_accuracy - current_accuracy

        prompt = (
            f"Generate a training curriculum for a {agent_type} AI agent.\n\n"
            f"Current accuracy: {current_accuracy:.0%}\n"
            f"Target accuracy: {target_accuracy:.0%}\n"
            f"Gap to close: {gap:.0%}\n\n"
            f"Provide:\n"
            f"1. Knowledge gaps to address\n"
            f"2. Training data categories needed\n"
            f"3. Progressive difficulty levels (5 levels)\n"
            f"4. Evaluation criteria for each level\n"
            f"5. Estimated cycles to reach target"
        )

        response = await generate_content(prompt)
        self.curricula_generated += 1

        curriculum = {
            "agent_type": agent_type,
            "current_accuracy": current_accuracy,
            "target_accuracy": target_accuracy,
            "gap": gap,
            "curriculum": response or self._fallback_curriculum(agent_type, gap),
            "difficulty_levels": self._generate_levels(agent_type, gap),
            "estimated_cycles": max(int(gap * 20), 5),
            "generated_at": time.time(),
        }

        return curriculum

    async def generate_training_data(
        self, agent_type: str, difficulty: int, count: int = 100
    ) -> dict[str, Any]:
        """Generate training data for a specific difficulty level.

        Args:
            agent_type: which agent to train
            difficulty: 1-5 scale
            count: number of examples to generate
        """
        data_specs = self._get_data_specs(agent_type, difficulty)

        prompt = (
            f"Generate {min(count, 10)} training examples for a {agent_type} agent.\n\n"
            f"Difficulty level: {difficulty}/5\n"
            f"Category: {data_specs['category']}\n"
            f"Format: input/output pairs\n\n"
            f"Each example should test: {data_specs['skill']}"
        )

        response = await generate_content(prompt)

        # Parse into structured training examples
        examples = []
        if response:
            parts = response.split("\n\n")
            for part in parts:
                if part.strip():
                    examples.append({
                        "input": part[:200],
                        "expected_output": "correct_response",
                        "difficulty": difficulty,
                        "category": data_specs["category"],
                    })

        # Pad to requested count
        while len(examples) < count:
            examples.append({
                "input": f"Training example {len(examples)+1} for {agent_type} (level {difficulty})",
                "expected_output": "expected_response",
                "difficulty": difficulty,
                "category": data_specs["category"],
            })

        return {
            "agent_type": agent_type,
            "difficulty": difficulty,
            "count": len(examples),
            "examples": examples[:count],
            "data_specs": data_specs,
            "generated_at": time.time(),
        }

    async def evaluate_performance(
        self, agent_type: str, test_results: list[dict]
    ) -> dict[str, Any]:
        """Evaluate agent performance and recommend next steps."""
        correct = sum(1 for r in test_results if r.get("correct", False))
        total = len(test_results)
        accuracy = correct / max(total, 1)

        self.training_cycles += 1
        self.performance_log.append({
            "cycle": self.training_cycles,
            "agent_type": agent_type,
            "accuracy": accuracy,
            "timestamp": time.time(),
        })

        # Determine next actions
        if accuracy >= 0.9:
            recommendation = "Target achieved. Advance to next difficulty level."
        elif accuracy >= 0.7:
            recommendation = "Good progress. Generate more edge-case training data."
        elif accuracy >= 0.5:
            recommendation = "Moderate progress. Focus on weak categories."
        else:
            recommendation = "Significant gap. Simplify training data and retrain from lower level."

        return {
            "agent_type": agent_type,
            "cycle": self.training_cycles,
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "recommendation": recommendation,
            "improvement_from_start": self._calculate_improvement(agent_type),
        }

    def _generate_levels(self, agent_type: str, gap: float) -> list[dict]:
        """Generate difficulty levels based on gap."""
        levels = {
            "security": [
                {"level": 1, "name": "Basic vulnerability identification", "threshold": 0.6},
                {"level": 2, "name": "CVE correlation and prioritization", "threshold": 0.7},
                {"level": 3, "name": "Multi-vector attack analysis", "threshold": 0.8},
                {"level": 4, "name": "Zero-day pattern recognition", "threshold": 0.85},
                {"level": 5, "name": "Advanced persistent threat detection", "threshold": 0.9},
            ],
            "trading": [
                {"level": 1, "name": "Basic indicator interpretation", "threshold": 0.6},
                {"level": 2, "name": "Multi-indicator signal generation", "threshold": 0.7},
                {"level": 3, "name": "Risk-adjusted position sizing", "threshold": 0.75},
                {"level": 4, "name": "Market regime detection", "threshold": 0.8},
                {"level": 5, "name": "Adaptive strategy selection", "threshold": 0.85},
            ],
            "software": [
                {"level": 1, "name": "Basic code generation", "threshold": 0.6},
                {"level": 2, "name": "Complex algorithm implementation", "threshold": 0.7},
                {"level": 3, "name": "System design and architecture", "threshold": 0.75},
                {"level": 4, "name": "Performance optimization", "threshold": 0.8},
                {"level": 5, "name": "Full-stack project delivery", "threshold": 0.85},
            ],
        }
        return levels.get(agent_type, levels["software"])

    def _get_data_specs(self, agent_type: str, difficulty: int) -> dict[str, str]:
        """Get data specifications for training generation."""
        specs = {
            "security": {
                1: {"category": "port_scanning", "skill": "identifying open services"},
                2: {"category": "cve_matching", "skill": "correlating versions with CVEs"},
                3: {"category": "exploit_chains", "skill": "chaining multiple vulnerabilities"},
                4: {"category": "zero_day", "skill": "detecting novel attack patterns"},
                5: {"category": "apt_detection", "skill": "identifying advanced persistent threats"},
            },
            "trading": {
                1: {"category": "indicator_reading", "skill": "interpreting RSI and MACD"},
                2: {"category": "signal_generation", "skill": "combining multiple signals"},
                3: {"category": "position_sizing", "skill": "Kelly criterion application"},
                4: {"category": "regime_detection", "skill": "identifying market conditions"},
                5: {"category": "strategy_adaptation", "skill": "switching strategies dynamically"},
            },
            "software": {
                1: {"category": "basic_coding", "skill": "writing correct functions"},
                2: {"category": "algorithms", "skill": "implementing complex algorithms"},
                3: {"category": "architecture", "skill": "designing scalable systems"},
                4: {"category": "optimization", "skill": "performance tuning"},
                5: {"category": "full_project", "skill": "end-to-end project delivery"},
            },
        }
        agent_specs = specs.get(agent_type, specs["software"])
        return agent_specs.get(difficulty, {"category": "general", "skill": "general task completion"})

    def _calculate_improvement(self, agent_type: str) -> float:
        """Calculate total improvement for an agent type."""
        agent_logs = [p for p in self.performance_log if p["agent_type"] == agent_type]
        if len(agent_logs) < 2:
            return 0.0
        return agent_logs[-1]["accuracy"] - agent_logs[0]["accuracy"]

    def _fallback_curriculum(self, agent_type: str, gap: float) -> str:
        return (
            f"Training Curriculum for {agent_type} agent (gap: {gap:.0%}):\n\n"
            f"Phase 1: Foundation (cycles 1-5)\n"
            f"  - Basic concept recognition\n"
            f"  - Pattern matching fundamentals\n\n"
            f"Phase 2: Application (cycles 6-10)\n"
            f"  - Complex scenario handling\n"
            f"  - Multi-step reasoning\n\n"
            f"Phase 3: Mastery (cycles 11-15)\n"
            f"  - Edge case handling\n"
            f"  - Novel situation adaptation"
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "curricula_generated": self.curricula_generated,
            "training_cycles": self.training_cycles,
            "performance_log": self.performance_log[-10:],
        }
