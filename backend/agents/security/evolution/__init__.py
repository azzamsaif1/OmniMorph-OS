"""Self-evolving penetration testing engine.

Surpasses single-model approaches (like Claude Mythos) through:
- Multi-agent specialized architecture
- Experience memory that persists across assessments
- Strategy learning from failures
- Continuous self-improvement without human intervention
"""

from backend.agents.security.evolution.experience_memory import ExperienceMemory
from backend.agents.security.evolution.strategy_learner import StrategyLearner
from backend.agents.security.evolution.evolution_engine import EvolutionEngine

__all__ = ["ExperienceMemory", "StrategyLearner", "EvolutionEngine"]
