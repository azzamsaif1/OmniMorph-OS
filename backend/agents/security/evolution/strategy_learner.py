"""Strategy Learner — learns and evolves attack strategies from experience.

Analyzes patterns in attack outcomes to:
- Identify which techniques work against which defenses
- Generate new attack strategies by combining successful tactics
- Adapt strategies when defenses change
- Predict success probability for untried approaches
- Continuously refine the attack playbook

Based on xOffense multi-agent framework (79.17% subtask completion)
and AutoPentester research (27% improvement in subtask completion).
"""

import time
import math
from typing import Any
from dataclasses import dataclass, field

from backend.agents.security.evolution.experience_memory import (
    ExperienceMemory, AttackExperience,
)


@dataclass
class AttackStrategy:
    """A learned attack strategy."""
    id: str
    name: str
    description: str
    target_type: str
    phases: list[dict] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    success_rate: float = 0.0
    times_used: int = 0
    times_succeeded: int = 0
    avg_duration_ms: float = 0.0
    defense_bypasses: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    generation: int = 1  # evolution generation


class StrategyLearner:
    """Learns and evolves attack strategies from accumulated experience.

    Capabilities:
    - Strategy synthesis: combines successful tactics into coherent strategies
    - Defense adaptation: generates bypass techniques for encountered defenses
    - Success prediction: estimates attack success probability
    - Strategy evolution: mutates and recombines strategies for improvement
    - Automatic retirement: removes consistently failing strategies
    """

    def __init__(self, memory: ExperienceMemory):
        self.memory = memory
        self.strategies: dict[str, AttackStrategy] = {}
        self.evolution_history: list[dict] = []
        self._min_confidence = 0.6
        self._retirement_threshold = 0.2  # retire if success < 20%
        self._evolution_generation = 0

        # Initialize base strategies from security knowledge
        self._init_base_strategies()

    def _init_base_strategies(self) -> None:
        """Initialize with known penetration testing strategies."""
        base_strategies = [
            {
                "id": "strat_network_recon",
                "name": "Network Reconnaissance",
                "description": "Systematic network scanning to discover hosts, ports, and services",
                "target_type": "network",
                "phases": [
                    {"step": 1, "action": "ping_sweep", "description": "Discover live hosts"},
                    {"step": 2, "action": "port_scan", "description": "Identify open ports (TCP SYN)"},
                    {"step": 3, "action": "service_detection", "description": "Identify service versions"},
                    {"step": 4, "action": "banner_grab", "description": "Collect service banners"},
                    {"step": 5, "action": "os_fingerprint", "description": "Determine operating system"},
                ],
                "prerequisites": ["network_access"],
                "success_rate": 0.95,
            },
            {
                "id": "strat_vuln_correlation",
                "name": "Vulnerability Correlation Attack",
                "description": "Correlate discovered services with CVE database to find exploitable vulnerabilities",
                "target_type": "service",
                "phases": [
                    {"step": 1, "action": "service_fingerprint", "description": "Exact version identification"},
                    {"step": 2, "action": "cve_lookup", "description": "Search CVE database for known vulns"},
                    {"step": 3, "action": "exploit_check", "description": "Verify exploit availability"},
                    {"step": 4, "action": "risk_score", "description": "Calculate CVSS risk score"},
                    {"step": 5, "action": "prioritize", "description": "Rank targets by exploitability"},
                ],
                "prerequisites": ["recon_complete"],
                "success_rate": 0.90,
            },
            {
                "id": "strat_service_exploit",
                "name": "Service Exploitation",
                "description": "Exploit known vulnerabilities in discovered services",
                "target_type": "service",
                "phases": [
                    {"step": 1, "action": "payload_select", "description": "Choose appropriate exploit payload"},
                    {"step": 2, "action": "payload_customize", "description": "Customize for target environment"},
                    {"step": 3, "action": "exploit_attempt", "description": "Execute exploit in safe mode"},
                    {"step": 4, "action": "verify_access", "description": "Confirm exploitation success"},
                    {"step": 5, "action": "document", "description": "Record technique and remediation"},
                ],
                "prerequisites": ["vuln_identified", "exploit_available"],
                "success_rate": 0.85,
            },
            {
                "id": "strat_defense_evasion",
                "name": "Defense Evasion",
                "description": "Bypass security controls like firewalls, IDS/IPS, WAF",
                "target_type": "network",
                "phases": [
                    {"step": 1, "action": "defense_detect", "description": "Identify active security controls"},
                    {"step": 2, "action": "traffic_analysis", "description": "Analyze allowed traffic patterns"},
                    {"step": 3, "action": "evasion_technique", "description": "Apply evasion (fragmentation, encoding, timing)"},
                    {"step": 4, "action": "verify_bypass", "description": "Confirm evasion success"},
                    {"step": 5, "action": "maintain_stealth", "description": "Continue operations covertly"},
                ],
                "prerequisites": ["defense_identified"],
                "success_rate": 0.65,
            },
            {
                "id": "strat_privilege_escalation",
                "name": "Privilege Escalation",
                "description": "Escalate from limited access to administrative privileges",
                "target_type": "host",
                "phases": [
                    {"step": 1, "action": "enumerate_privs", "description": "Check current privilege level"},
                    {"step": 2, "action": "find_misconfigs", "description": "Search for misconfigurations"},
                    {"step": 3, "action": "kernel_check", "description": "Check for kernel exploits"},
                    {"step": 4, "action": "escalate", "description": "Attempt privilege escalation"},
                    {"step": 5, "action": "verify_root", "description": "Confirm elevated access"},
                ],
                "prerequisites": ["initial_access"],
                "success_rate": 0.70,
            },
            {
                "id": "strat_lateral_movement",
                "name": "Lateral Movement",
                "description": "Move across the network to reach high-value targets",
                "target_type": "network",
                "phases": [
                    {"step": 1, "action": "credential_harvest", "description": "Extract credentials from compromised host"},
                    {"step": 2, "action": "internal_recon", "description": "Scan internal network segments"},
                    {"step": 3, "action": "pivot", "description": "Use compromised host as pivot point"},
                    {"step": 4, "action": "move_lateral", "description": "Access adjacent systems"},
                    {"step": 5, "action": "establish_persistence", "description": "Maintain access on new hosts"},
                ],
                "prerequisites": ["initial_access", "elevated_privileges"],
                "success_rate": 0.60,
            },
        ]

        for s in base_strategies:
            strategy = AttackStrategy(
                id=s["id"],
                name=s["name"],
                description=s["description"],
                target_type=s["target_type"],
                phases=s["phases"],
                prerequisites=s.get("prerequisites", []),
                success_rate=s.get("success_rate", 0.5),
            )
            self.strategies[strategy.id] = strategy

    def learn_from_experience(self, experience: AttackExperience) -> dict[str, Any]:
        """Learn from a single experience and update strategies."""
        updates = {
            "strategy_updates": [],
            "new_strategies": [],
            "retired_strategies": [],
            "defense_adaptations": [],
        }

        # Find matching strategies
        matching = self._find_matching_strategies(experience)

        for strategy in matching:
            # Update success rate
            strategy.times_used += 1
            if experience.outcome == "success":
                strategy.times_succeeded += 1
            strategy.success_rate = strategy.times_succeeded / max(strategy.times_used, 1)

            # Update average duration
            if experience.duration_ms > 0:
                n = strategy.times_used
                strategy.avg_duration_ms = (
                    (strategy.avg_duration_ms * (n - 1) + experience.duration_ms) / n
                )

            strategy.last_updated = time.time()
            updates["strategy_updates"].append({
                "strategy_id": strategy.id,
                "new_success_rate": strategy.success_rate,
                "times_used": strategy.times_used,
            })

            # Learn defense bypasses
            if experience.outcome == "success" and experience.defenses_encountered:
                for defense in experience.defenses_encountered:
                    for tactic in experience.tactics_used:
                        strategy.defense_bypasses[defense] = tactic
                        updates["defense_adaptations"].append({
                            "defense": defense,
                            "bypass_tactic": tactic,
                            "strategy": strategy.id,
                        })

            # Retire consistently failing strategies
            if (strategy.times_used >= 5 and
                    strategy.success_rate < self._retirement_threshold):
                updates["retired_strategies"].append({
                    "strategy_id": strategy.id,
                    "reason": f"Success rate {strategy.success_rate:.0%} below threshold",
                })

        # Check if we can synthesize a new strategy
        new_strategy = self._try_synthesize_strategy(experience)
        if new_strategy:
            self.strategies[new_strategy.id] = new_strategy
            updates["new_strategies"].append({
                "strategy_id": new_strategy.id,
                "name": new_strategy.name,
                "derived_from": "experience_synthesis",
            })

        return updates

    def _find_matching_strategies(
        self, experience: AttackExperience
    ) -> list[AttackStrategy]:
        """Find strategies that match the experience."""
        matching = []
        for strategy in self.strategies.values():
            if strategy.target_type == experience.target_type:
                matching.append(strategy)
            elif any(
                phase["action"] == experience.technique
                for phase in strategy.phases
            ):
                matching.append(strategy)
        return matching

    def _try_synthesize_strategy(
        self, experience: AttackExperience
    ) -> AttackStrategy | None:
        """Try to synthesize a new strategy from accumulated experiences."""
        # Need enough experiences to synthesize
        similar = self.memory.find_similar_experiences(
            experience.target_type, experience.technique
        )
        if len(similar) < 3:
            return None

        # Only synthesize from successful experiences
        successful = [e for e in similar if e.outcome == "success"]
        if len(successful) < 2:
            return None

        # Check if we already have a strategy for this combination
        existing_ids = {s.id for s in self.strategies.values()}
        new_id = f"strat_synth_{experience.target_type}_{experience.technique}"
        if new_id in existing_ids:
            return None

        # Combine successful tactics into phases
        all_tactics = []
        for exp in successful:
            all_tactics.extend(exp.tactics_used)

        # Count tactic frequencies
        tactic_counts: dict[str, int] = {}
        for tactic in all_tactics:
            tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1

        # Build phases from most common tactics
        top_tactics = sorted(tactic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        phases = [
            {"step": i + 1, "action": tactic, "description": f"Auto-learned: {tactic}"}
            for i, (tactic, _) in enumerate(top_tactics)
        ]

        if not phases:
            return None

        self._evolution_generation += 1
        return AttackStrategy(
            id=new_id,
            name=f"Synthesized: {experience.target_type} via {experience.technique}",
            description=f"Auto-generated strategy from {len(successful)} successful experiences",
            target_type=experience.target_type,
            phases=phases,
            success_rate=len(successful) / max(len(similar), 1),
            generation=self._evolution_generation,
        )

    def evolve_strategies(self) -> dict[str, Any]:
        """Run one evolution cycle — mutate, recombine, and select strategies."""
        self._evolution_generation += 1
        results = {
            "generation": self._evolution_generation,
            "mutations": [],
            "retirements": [],
            "improvements": [],
        }

        strategies_list = list(self.strategies.values())
        if len(strategies_list) < 2:
            return results

        # Sort by success rate
        ranked = sorted(strategies_list, key=lambda s: s.success_rate, reverse=True)

        # Top performers stay, bottom performers get mutated or retired
        top_half = ranked[:len(ranked) // 2 + 1]
        bottom_half = ranked[len(ranked) // 2 + 1:]

        for strategy in bottom_half:
            if strategy.times_used >= 5 and strategy.success_rate < self._retirement_threshold:
                results["retirements"].append({
                    "id": strategy.id,
                    "name": strategy.name,
                    "success_rate": strategy.success_rate,
                })
                continue

            # Mutate: borrow a phase from a top performer
            if top_half:
                donor = top_half[0]
                if donor.phases and strategy.phases:
                    # Add a successful phase from the donor
                    borrowed_phase = donor.phases[-1].copy()
                    borrowed_phase["step"] = len(strategy.phases) + 1
                    borrowed_phase["description"] = f"Evolved from {donor.name}: {borrowed_phase['description']}"
                    strategy.phases.append(borrowed_phase)
                    strategy.generation = self._evolution_generation
                    strategy.last_updated = time.time()

                    results["mutations"].append({
                        "strategy_id": strategy.id,
                        "mutation": f"Borrowed phase from {donor.name}",
                        "new_phase_count": len(strategy.phases),
                    })

        # Record evolution event
        self.evolution_history.append({
            "generation": self._evolution_generation,
            "timestamp": time.time(),
            "total_strategies": len(self.strategies),
            "avg_success_rate": sum(s.success_rate for s in self.strategies.values()) / max(len(self.strategies), 1),
            "mutations": len(results["mutations"]),
            "retirements": len(results["retirements"]),
        })

        return results

    def predict_success(
        self, target_type: str, technique: str, defenses: list[str] | None = None
    ) -> dict[str, Any]:
        """Predict success probability for an attack approach."""
        # Base prediction from patterns
        recommendation = self.memory.get_recommended_approach(target_type, technique)
        base_confidence = recommendation.get("confidence", 0.5)

        # Adjust for known defenses
        defense_penalty = 0.0
        bypasses_available = []

        if defenses:
            for defense in defenses:
                # Check if we have a bypass
                has_bypass = False
                for strategy in self.strategies.values():
                    if defense in strategy.defense_bypasses:
                        has_bypass = True
                        bypasses_available.append({
                            "defense": defense,
                            "bypass": strategy.defense_bypasses[defense],
                            "source_strategy": strategy.id,
                        })
                        break

                if not has_bypass:
                    defense_penalty += 0.15  # Each unbypassable defense reduces confidence

        adjusted_confidence = max(0.05, base_confidence - defense_penalty)

        # Factor in strategy success rates
        matching_strategies = [
            s for s in self.strategies.values()
            if s.target_type == target_type and s.times_used > 0
        ]
        if matching_strategies:
            avg_strategy_success = sum(
                s.success_rate for s in matching_strategies
            ) / len(matching_strategies)
            adjusted_confidence = (adjusted_confidence + avg_strategy_success) / 2

        return {
            "predicted_success": adjusted_confidence,
            "base_confidence": base_confidence,
            "defense_penalty": defense_penalty,
            "bypasses_available": bypasses_available,
            "recommendation": recommendation["recommendation"],
            "matching_strategies": len(matching_strategies),
            "suggested_approach": recommendation.get("suggested_tactics", []),
        }

    def get_best_strategy(self, target_type: str) -> AttackStrategy | None:
        """Get the best strategy for a given target type."""
        candidates = [
            s for s in self.strategies.values()
            if s.target_type == target_type and s.success_rate >= self._min_confidence
        ]
        if not candidates:
            # Fall back to any strategy for this type
            candidates = [
                s for s in self.strategies.values()
                if s.target_type == target_type
            ]
        if not candidates:
            return None

        return max(candidates, key=lambda s: s.success_rate)

    def get_stats(self) -> dict[str, Any]:
        """Get strategy learner statistics."""
        strategies = list(self.strategies.values())
        return {
            "total_strategies": len(strategies),
            "avg_success_rate": sum(s.success_rate for s in strategies) / max(len(strategies), 1),
            "evolution_generation": self._evolution_generation,
            "evolution_cycles": len(self.evolution_history),
            "strategies_by_type": {
                target_type: len([s for s in strategies if s.target_type == target_type])
                for target_type in {s.target_type for s in strategies}
            },
            "top_strategies": [
                {"id": s.id, "name": s.name, "success_rate": s.success_rate, "times_used": s.times_used}
                for s in sorted(strategies, key=lambda x: x.success_rate, reverse=True)[:5]
            ],
            "total_defense_bypasses": sum(
                len(s.defense_bypasses) for s in strategies
            ),
        }
