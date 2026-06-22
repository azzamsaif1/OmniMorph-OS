"""Security self-evolution — learns from assessment failures and updates strategies.

Analyzes failed exploitation attempts and adjusts attack patterns.
"""

import time
from typing import Any


class SecurityEvolver:
    """Self-evolution for the security agent.

    After each assessment:
    1. Analyze failed detections
    2. Identify new patterns
    3. Update scanning strategies
    4. Improve exploit payload generation
    5. Track improvement over time
    """

    def __init__(self):
        self.evolution_log: list[dict] = []
        self.learned_patterns: list[dict] = []
        self.strategy_updates: list[str] = []
        self.accuracy_history: list[float] = []

    def analyze_failures(self, assessment_results: dict) -> dict[str, Any]:
        """Analyze assessment results and identify improvement areas."""
        report = assessment_results.get("report", {})
        exploits = assessment_results.get("exploit_simulation", [])

        failed_exploits = [e for e in exploits if not e.get("success", False)]
        missed_vulns = report.get("total_vulnerabilities", 0) - report.get("exploitable_count", 0)

        analysis = {
            "total_vulns_found": report.get("total_vulnerabilities", 0),
            "exploitable": report.get("exploitable_count", 0),
            "failed_exploits": len(failed_exploits),
            "missed_vulns": missed_vulns,
            "improvement_areas": [],
            "new_strategies": [],
        }

        # Identify improvement areas
        if missed_vulns > 0:
            analysis["improvement_areas"].append(
                f"Expand CVE database coverage ({missed_vulns} unmatched vulnerabilities)"
            )
        if failed_exploits:
            analysis["improvement_areas"].append(
                f"Improve payload generation ({len(failed_exploits)} failed attempts)"
            )
        if report.get("open_ports", 0) < 5:
            analysis["new_strategies"].append(
                "Consider full port range scan for targets with few common open ports"
            )

        self.evolution_log.append(analysis)
        return analysis

    def update_strategies(self, analysis: dict) -> list[str]:
        """Update attack strategies based on analysis."""
        updates = []

        for area in analysis.get("improvement_areas", []):
            strategy = f"Strategy update [{time.strftime('%Y%m%d')}]: {area}"
            updates.append(strategy)
            self.strategy_updates.append(strategy)

        for strategy in analysis.get("new_strategies", []):
            self.strategy_updates.append(strategy)
            updates.append(strategy)

        return updates

    def track_accuracy(self, detection_rate: float) -> dict[str, Any]:
        """Track detection accuracy over time."""
        self.accuracy_history.append(detection_rate)

        improvement = 0.0
        if len(self.accuracy_history) >= 2:
            improvement = self.accuracy_history[-1] - self.accuracy_history[-2]

        return {
            "current_accuracy": detection_rate,
            "improvement": improvement,
            "history_length": len(self.accuracy_history),
            "target_accuracy": 0.95,
            "gap": 0.95 - detection_rate,
            "on_track": detection_rate >= 0.90 or improvement > 0,
        }

    def get_evolution_summary(self) -> dict[str, Any]:
        """Get summary of all evolution cycles."""
        return {
            "total_evolutions": len(self.evolution_log),
            "learned_patterns": len(self.learned_patterns),
            "strategy_updates": len(self.strategy_updates),
            "accuracy_history": self.accuracy_history[-10:],
            "latest_strategies": self.strategy_updates[-5:],
        }
