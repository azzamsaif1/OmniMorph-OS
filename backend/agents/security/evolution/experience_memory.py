"""Experience Memory — stores and retrieves attack experiences for learning.

Maintains a persistent record of all penetration testing activities including:
- Successful attacks (tactics, techniques, procedures)
- Failed attempts (why they failed, what defenses were encountered)
- Discovered patterns (common configurations, defense signatures)
- Environmental fingerprints (OS types, network topologies)

This enables the system to learn from every assessment and improve over time.
"""

import time
import hashlib
from typing import Any
from dataclasses import dataclass, field


@dataclass
class AttackExperience:
    """Single attack experience record."""
    id: str
    timestamp: float
    target_type: str  # network|host|service|application
    technique: str  # scan|exploit|bruteforce|social_engineering
    target_info: dict = field(default_factory=dict)
    outcome: str = "unknown"  # success|failure|partial|blocked
    confidence: float = 0.0
    defenses_encountered: list[str] = field(default_factory=list)
    tactics_used: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    next_steps: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class ExperienceMemory:
    """Stores and retrieves attack experiences for continuous learning.

    Features:
    - Temporal decay: older experiences weighted less
    - Pattern recognition: identifies recurring success/failure patterns
    - Strategy extraction: derives high-level strategies from experiences
    - Similarity search: finds relevant past experiences for new targets
    """

    def __init__(self):
        self.experiences: list[AttackExperience] = []
        self.patterns: dict[str, dict] = {}
        self.success_strategies: list[dict] = []
        self.failure_patterns: list[dict] = []
        self._pattern_threshold: int = 3  # min occurrences to form pattern

    def record_experience(
        self,
        target_type: str,
        technique: str,
        outcome: str,
        target_info: dict | None = None,
        defenses_encountered: list[str] | None = None,
        tactics_used: list[str] | None = None,
        lessons_learned: list[str] | None = None,
        duration_ms: float = 0.0,
        confidence: float = 0.0,
        metadata: dict | None = None,
    ) -> AttackExperience:
        """Record a new attack experience."""
        exp_id = hashlib.sha256(
            f"{time.time()}:{target_type}:{technique}:{outcome}".encode()
        ).hexdigest()[:16]

        experience = AttackExperience(
            id=exp_id,
            timestamp=time.time(),
            target_type=target_type,
            technique=technique,
            outcome=outcome,
            target_info=target_info or {},
            defenses_encountered=defenses_encountered or [],
            tactics_used=tactics_used or [],
            lessons_learned=lessons_learned or [],
            duration_ms=duration_ms,
            confidence=confidence,
            metadata=metadata or {},
        )

        self.experiences.append(experience)
        self._update_patterns(experience)
        return experience

    def _update_patterns(self, exp: AttackExperience) -> None:
        """Update pattern recognition from new experience."""
        # Track technique-outcome patterns
        key = f"{exp.technique}:{exp.target_type}"
        if key not in self.patterns:
            self.patterns[key] = {
                "total": 0, "successes": 0, "failures": 0,
                "avg_confidence": 0.0, "common_defenses": {},
                "effective_tactics": {},
            }

        pattern = self.patterns[key]
        pattern["total"] += 1
        if exp.outcome == "success":
            pattern["successes"] += 1
        elif exp.outcome in ("failure", "blocked"):
            pattern["failures"] += 1

        # Update running average confidence
        n = pattern["total"]
        pattern["avg_confidence"] = (
            (pattern["avg_confidence"] * (n - 1) + exp.confidence) / n
        )

        # Track defense frequencies
        for defense in exp.defenses_encountered:
            pattern["common_defenses"][defense] = (
                pattern["common_defenses"].get(defense, 0) + 1
            )

        # Track effective tactics
        if exp.outcome == "success":
            for tactic in exp.tactics_used:
                pattern["effective_tactics"][tactic] = (
                    pattern["effective_tactics"].get(tactic, 0) + 1
                )

        # Extract strategies from patterns
        if pattern["total"] >= self._pattern_threshold:
            self._extract_strategies(key, pattern)

    def _extract_strategies(self, key: str, pattern: dict) -> None:
        """Extract high-level strategies from accumulated patterns."""
        success_rate = pattern["successes"] / max(pattern["total"], 1)

        if success_rate >= 0.7:
            # High success — record as a winning strategy
            top_tactics = sorted(
                pattern["effective_tactics"].items(),
                key=lambda x: x[1], reverse=True
            )[:5]

            strategy = {
                "pattern_key": key,
                "success_rate": success_rate,
                "recommended_tactics": [t[0] for t in top_tactics],
                "avg_confidence": pattern["avg_confidence"],
                "sample_size": pattern["total"],
                "extracted_at": time.time(),
            }

            # Avoid duplicates
            existing = [s for s in self.success_strategies if s["pattern_key"] == key]
            if existing:
                existing[0].update(strategy)
            else:
                self.success_strategies.append(strategy)

        elif success_rate <= 0.3 and pattern["total"] >= self._pattern_threshold:
            # Low success — record as a failure pattern
            top_defenses = sorted(
                pattern["common_defenses"].items(),
                key=lambda x: x[1], reverse=True
            )[:5]

            failure = {
                "pattern_key": key,
                "failure_rate": 1 - success_rate,
                "blocking_defenses": [d[0] for d in top_defenses],
                "sample_size": pattern["total"],
                "avoid_unless": "defenses are bypassed or alternative approach found",
                "extracted_at": time.time(),
            }

            existing = [f for f in self.failure_patterns if f["pattern_key"] == key]
            if existing:
                existing[0].update(failure)
            else:
                self.failure_patterns.append(failure)

    def find_similar_experiences(
        self, target_type: str, technique: str, target_info: dict | None = None
    ) -> list[AttackExperience]:
        """Find past experiences similar to the current situation."""
        candidates = []
        for exp in self.experiences:
            score = 0.0
            if exp.target_type == target_type:
                score += 0.4
            if exp.technique == technique:
                score += 0.3
            if target_info and exp.target_info:
                # Check for matching services/ports
                if exp.target_info.get("service") == target_info.get("service"):
                    score += 0.2
                if exp.target_info.get("os") == target_info.get("os"):
                    score += 0.1

            # Apply temporal decay (recent experiences weighted more)
            age_hours = (time.time() - exp.timestamp) / 3600
            decay = max(0.5, 1.0 - (age_hours / 720))  # 30-day half-life
            score *= decay

            if score >= 0.3:
                candidates.append((score, exp))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in candidates[:10]]

    def get_recommended_approach(
        self, target_type: str, technique: str
    ) -> dict[str, Any]:
        """Get recommended approach based on accumulated experience."""
        key = f"{technique}:{target_type}"
        pattern = self.patterns.get(key)

        if not pattern or pattern["total"] < self._pattern_threshold:
            return {
                "recommendation": "explore",
                "reason": "Insufficient data — try multiple approaches",
                "confidence": 0.2,
                "suggested_tactics": [],
            }

        success_rate = pattern["successes"] / max(pattern["total"], 1)

        if success_rate >= 0.7:
            top_tactics = sorted(
                pattern["effective_tactics"].items(),
                key=lambda x: x[1], reverse=True
            )[:3]
            return {
                "recommendation": "proceed",
                "reason": f"High success rate ({success_rate:.0%}) from {pattern['total']} attempts",
                "confidence": pattern["avg_confidence"],
                "suggested_tactics": [t[0] for t in top_tactics],
                "expected_defenses": list(pattern["common_defenses"].keys())[:3],
            }
        elif success_rate <= 0.3:
            return {
                "recommendation": "avoid_or_adapt",
                "reason": f"Low success rate ({success_rate:.0%}) — defenses likely blocking",
                "confidence": 0.3,
                "blocking_defenses": list(pattern["common_defenses"].keys())[:5],
                "alternative": "Try different technique or bypass defenses first",
            }
        else:
            return {
                "recommendation": "proceed_with_caution",
                "reason": f"Mixed results ({success_rate:.0%}) — outcome uncertain",
                "confidence": pattern["avg_confidence"],
                "suggested_tactics": list(pattern["effective_tactics"].keys())[:3],
                "known_defenses": list(pattern["common_defenses"].keys())[:3],
            }

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        total = len(self.experiences)
        successes = sum(1 for e in self.experiences if e.outcome == "success")
        failures = sum(1 for e in self.experiences if e.outcome in ("failure", "blocked"))

        return {
            "total_experiences": total,
            "success_count": successes,
            "failure_count": failures,
            "success_rate": successes / max(total, 1),
            "patterns_identified": len(self.patterns),
            "success_strategies": len(self.success_strategies),
            "failure_patterns": len(self.failure_patterns),
            "unique_techniques": len({e.technique for e in self.experiences}),
            "unique_target_types": len({e.target_type for e in self.experiences}),
        }
