"""Self-evolver agent — MUSE-style memory and experience transformation.

After each research cycle, reverses the path and transforms findings
into structured experience for the agent system.

Source: MUSE Memory Module — update memory every 6 hours.
"""

import time
from typing import Any

from backend.gemini_client import generate_content


class SelfEvolver:
    """MUSE-style self-evolution engine.

    Cycle: Gather → Reflect → Transform → Integrate → Evaluate
    - Gather: collect new research findings
    - Reflect: reverse the discovery path (what led to each insight)
    - Transform: convert into structured training experiences
    - Integrate: update the knowledge base with new experiences
    - Evaluate: measure knowledge improvement per cycle
    """

    def __init__(self):
        self.memory: list[dict] = []
        self.experiences: list[dict] = []
        self.evolution_cycles: int = 0
        self.improvement_history: list[float] = []
        self.last_evolution_time: float = 0
        self.cycle_interval_hours: float = 6.0

    async def evolve(self, new_knowledge: list[dict]) -> dict[str, Any]:
        """Execute one evolution cycle on new knowledge.

        MUSE technique: reverse the path, transform into structured experience.
        """
        cycle_start = time.time()
        self.evolution_cycles += 1

        # Stage 1: Reflect — analyze what patterns emerge
        reflections = await self._reflect(new_knowledge)

        # Stage 2: Reverse path — trace back from insights to fundamentals
        reversed_path = await self._reverse_path(new_knowledge, reflections)

        # Stage 3: Transform — create structured experiences
        experiences = await self._transform(reversed_path)

        # Stage 4: Integrate — merge into existing memory
        integration_result = self._integrate(experiences)

        # Stage 5: Evaluate — measure improvement
        improvement = self._evaluate()

        self.last_evolution_time = time.time()

        return {
            "cycle": self.evolution_cycles,
            "duration_seconds": time.time() - cycle_start,
            "new_knowledge_items": len(new_knowledge),
            "reflections_generated": len(reflections),
            "experiences_created": len(experiences),
            "integration": integration_result,
            "improvement_score": improvement,
            "total_memory_size": len(self.memory),
            "next_evolution_in": f"{self.cycle_interval_hours}h",
        }

    async def _reflect(self, knowledge: list[dict]) -> list[dict[str, str]]:
        """Stage 1: Reflect on new knowledge — find patterns and connections."""
        if not knowledge:
            return []

        titles = [k.get("paper_title", k.get("title", "")) for k in knowledge[:10]]
        titles_text = "\n".join(f"- {t}" for t in titles if t)

        prompt = (
            f"Given these recent research findings, identify 3 emerging patterns "
            f"and their implications for AI agent systems:\n\n{titles_text}\n\n"
            f"For each pattern: name, description, implication for agents."
        )

        response = await generate_content(prompt)

        reflections = []
        if response:
            # Parse response into reflections
            for line in response.strip().split("\n"):
                if line.strip():
                    reflections.append({
                        "pattern": line.strip()[:100],
                        "source_count": len(knowledge),
                        "timestamp": time.time(),
                    })

        # Ensure minimum reflections
        while len(reflections) < 3:
            reflections.append({
                "pattern": f"Cross-domain applicability of research batch ({len(knowledge)} papers)",
                "source_count": len(knowledge),
                "timestamp": time.time(),
            })

        return reflections[:5]

    async def _reverse_path(
        self, knowledge: list[dict], reflections: list[dict]
    ) -> list[dict[str, Any]]:
        """Stage 2: MUSE reverse path — trace from insights back to fundamentals.

        For each reflection, identify:
        - What fundamental concept enables this pattern
        - What building blocks are required
        - What the learning sequence should be (reversed)
        """
        reversed_paths = []

        for reflection in reflections:
            pattern = reflection.get("pattern", "")
            path = {
                "pattern": pattern,
                "fundamentals": [],
                "building_blocks": [],
                "learning_sequence": [],
            }

            prompt = (
                f"For the research pattern: '{pattern}'\n\n"
                f"Identify:\n"
                f"1. The 3 fundamental concepts that enable this\n"
                f"2. The building blocks required (list of 3)\n"
                f"3. The optimal learning sequence (reversed, from advanced to basic)"
            )

            response = await generate_content(prompt)

            if response:
                lines = [l.strip() for l in response.split("\n") if l.strip()]
                # Distribute lines across categories
                section = "fundamentals"
                for line in lines:
                    cleaned = line.lstrip("0123456789.-) ").strip()
                    if not cleaned:
                        continue
                    if "building" in line.lower() or "block" in line.lower():
                        section = "building_blocks"
                    elif "sequence" in line.lower() or "learning" in line.lower():
                        section = "learning_sequence"
                    elif cleaned:
                        path[section].append(cleaned[:150])

            # Ensure non-empty
            if not path["fundamentals"]:
                path["fundamentals"] = ["Core mathematical foundations", "Distributed systems theory", "Learning theory"]
            if not path["building_blocks"]:
                path["building_blocks"] = ["Neural architecture", "Training pipeline", "Evaluation framework"]
            if not path["learning_sequence"]:
                path["learning_sequence"] = ["Advanced applications", "Core algorithms", "Fundamental theory"]

            reversed_paths.append(path)

        return reversed_paths

    async def _transform(self, reversed_paths: list[dict]) -> list[dict[str, Any]]:
        """Stage 3: Transform reversed paths into structured training experiences."""
        experiences = []

        for path in reversed_paths:
            # Create experience from each path
            experience = {
                "id": f"exp_{self.evolution_cycles}_{len(experiences)}",
                "pattern": path["pattern"],
                "type": "research_insight",
                "fundamentals": path["fundamentals"],
                "building_blocks": path["building_blocks"],
                "learning_sequence": path["learning_sequence"],
                "difficulty": self._assess_difficulty(path),
                "relevance_score": self._assess_relevance(path),
                "created_at": time.time(),
                "cycle": self.evolution_cycles,
            }
            experiences.append(experience)

        self.experiences.extend(experiences)
        return experiences

    def _integrate(self, new_experiences: list[dict]) -> dict[str, Any]:
        """Stage 4: Integrate new experiences into memory."""
        before_size = len(self.memory)

        for exp in new_experiences:
            # Check for duplicates (by pattern similarity)
            is_duplicate = any(
                m.get("pattern", "") == exp["pattern"]
                for m in self.memory
            )
            if not is_duplicate:
                self.memory.append(exp)

        after_size = len(self.memory)
        new_items = after_size - before_size

        return {
            "memory_before": before_size,
            "memory_after": after_size,
            "new_items_added": new_items,
            "duplicates_skipped": len(new_experiences) - new_items,
        }

    def _evaluate(self) -> float:
        """Stage 5: Evaluate improvement from this cycle."""
        # Simple metric: knowledge growth rate
        if len(self.improvement_history) == 0:
            improvement = 1.0
        else:
            prev = self.improvement_history[-1]
            current = len(self.memory)
            improvement = (current - prev) / max(prev, 1)

        self.improvement_history.append(len(self.memory))

        # Target: 10% improvement per cycle (from ALAS: 15% → 90%)
        return min(improvement, 1.0)

    def _assess_difficulty(self, path: dict) -> str:
        """Assess difficulty level of a learning path."""
        seq_len = len(path.get("learning_sequence", []))
        if seq_len > 5:
            return "advanced"
        elif seq_len > 3:
            return "intermediate"
        return "beginner"

    def _assess_relevance(self, path: dict) -> float:
        """Assess relevance of path to our agent system (0-1)."""
        relevant_keywords = [
            "agent", "multi-agent", "learning", "security", "trading",
            "cognitive", "adaptive", "self-evolving", "federated",
        ]
        text = " ".join(path.get("fundamentals", []) + path.get("building_blocks", []))
        text = text.lower()

        matches = sum(1 for kw in relevant_keywords if kw in text)
        return min(matches / 5.0, 1.0)

    def should_evolve(self) -> bool:
        """Check if it's time for the next evolution cycle."""
        if self.last_evolution_time == 0:
            return True
        elapsed_hours = (time.time() - self.last_evolution_time) / 3600
        return elapsed_hours >= self.cycle_interval_hours

    def get_evolution_stats(self) -> dict[str, Any]:
        """Get evolution history and performance metrics."""
        return {
            "total_cycles": self.evolution_cycles,
            "total_memory_items": len(self.memory),
            "total_experiences": len(self.experiences),
            "improvement_history": self.improvement_history[-10:],
            "avg_improvement": (
                sum(self.improvement_history) / len(self.improvement_history)
                if self.improvement_history else 0.0
            ),
            "last_evolution": self.last_evolution_time,
            "next_evolution_due": self.should_evolve(),
        }
