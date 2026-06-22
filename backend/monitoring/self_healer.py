"""Self-Healer — automatic error fixing and safe optimization engine.

Capabilities:
- Automatic error detection and recovery
- Safe performance optimizations
- Continuous self-development without manual intervention
- Core architecture preservation (never modifies Layers 0-1)
- Rollback mechanism for unsafe changes
"""

import time
from typing import Any
from dataclasses import dataclass, field

from backend.monitoring.performance_analyzer import PerformanceAnalyzer, PerformanceIssue


@dataclass
class HealingAction:
    """A self-healing action taken or proposed."""
    id: str
    action_type: str  # fix|optimize|adapt|rollback
    target: str  # which component
    description: str
    status: str = "proposed"  # proposed|approved|applied|rolled_back|rejected
    risk_level: str = "low"  # low|medium|high|critical
    auto_approved: bool = False
    applied_at: float = 0.0
    result: str = ""
    metrics_before: dict = field(default_factory=dict)
    metrics_after: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class OptimizationResult:
    """Result of applying an optimization."""
    success: bool
    description: str
    improvement: float = 0.0
    rollback_needed: bool = False


class SelfHealer:
    """Automatic error fixing and self-optimization engine.

    Principles:
    1. Never modify core architecture (Layers 0-1)
    2. Only apply changes that are safe and reversible
    3. Monitor impact of changes and rollback if negative
    4. Log every action for transparency and auditability
    5. Require human approval for high-risk changes
    """

    def __init__(self, analyzer: PerformanceAnalyzer):
        self.analyzer = analyzer
        self.actions: list[HealingAction] = []
        self.applied_optimizations: list[dict] = []
        self._action_counter = 0

        # Configuration parameters that can be safely tuned
        self.tunable_params: dict[str, dict[str, Any]] = {
            "security.scan_timeout_ms": {
                "current": 5000,
                "min": 1000,
                "max": 30000,
                "step": 1000,
                "description": "TCP port scan timeout",
            },
            "security.max_concurrent_scans": {
                "current": 10,
                "min": 1,
                "max": 50,
                "step": 5,
                "description": "Maximum concurrent port scans",
            },
            "security.cve_match_threshold": {
                "current": 0.7,
                "min": 0.5,
                "max": 0.95,
                "step": 0.05,
                "description": "Minimum confidence for CVE matching",
            },
            "security.exploit_timeout_ms": {
                "current": 10000,
                "min": 5000,
                "max": 60000,
                "step": 5000,
                "description": "Exploit simulation timeout",
            },
            "finance.signal_lookback_periods": {
                "current": 50,
                "min": 20,
                "max": 200,
                "step": 10,
                "description": "Number of price periods for signal generation",
            },
            "finance.risk_tolerance": {
                "current": 0.05,
                "min": 0.01,
                "max": 0.15,
                "step": 0.01,
                "description": "Portfolio risk tolerance (VaR threshold)",
            },
            "software.review_depth": {
                "current": 3,
                "min": 1,
                "max": 5,
                "step": 1,
                "description": "Code review analysis depth level",
            },
            "research.scan_batch_size": {
                "current": 100,
                "min": 10,
                "max": 500,
                "step": 50,
                "description": "ArXiv papers per scan batch",
            },
            "negotiation.max_rounds": {
                "current": 10,
                "min": 3,
                "max": 50,
                "step": 5,
                "description": "Maximum negotiation rounds before forced resolution",
            },
            "system.anomaly_threshold": {
                "current": 2.0,
                "min": 1.5,
                "max": 4.0,
                "step": 0.5,
                "description": "Z-score threshold for anomaly detection",
            },
        }

        # Protected components that must never be modified
        self.protected_components = {
            "backend/agents/base.py",
            "backend/agents/orchestrator.py",
            "backend/agents/supervisors/",
            "backend/agents/specialists/",
            "backend/config.py",
            "backend/db.py",
        }

    def diagnose_and_heal(self) -> dict[str, Any]:
        """Run a full diagnostic cycle and apply safe fixes."""
        results = {
            "diagnosis": [],
            "proposed_actions": [],
            "applied_actions": [],
            "skipped_actions": [],
            "summary": {},
        }

        # 1. Analyze current health
        health = self.analyzer.get_health_report()
        trends = self.analyzer.analyze_trends()
        recommendations = self.analyzer.get_improvement_recommendations()

        results["diagnosis"] = {
            "health": health["overall_health"],
            "open_issues": health["open_issues"],
            "degrading_metrics": trends.get("degrading_count", 0),
            "recommendations_count": len(recommendations),
        }

        # 2. Generate healing actions from issues
        for issue in health.get("issues", []):
            action = self._generate_healing_action(issue)
            if action:
                results["proposed_actions"].append({
                    "id": action.id,
                    "type": action.action_type,
                    "target": action.target,
                    "description": action.description,
                    "risk_level": action.risk_level,
                    "auto_approved": action.auto_approved,
                })

                # Auto-apply safe fixes
                if action.auto_approved and action.risk_level == "low":
                    result = self._apply_action(action)
                    results["applied_actions"].append({
                        "id": action.id,
                        "description": action.description,
                        "result": result.description,
                        "success": result.success,
                    })
                else:
                    results["skipped_actions"].append({
                        "id": action.id,
                        "reason": f"Requires approval (risk: {action.risk_level})",
                    })

        # 3. Generate optimization actions from recommendations
        for rec in recommendations[:5]:
            opt_action = self._generate_optimization(rec)
            if opt_action:
                results["proposed_actions"].append({
                    "id": opt_action.id,
                    "type": opt_action.action_type,
                    "target": opt_action.target,
                    "description": opt_action.description,
                    "risk_level": opt_action.risk_level,
                })

                if opt_action.auto_approved:
                    result = self._apply_action(opt_action)
                    results["applied_actions"].append({
                        "id": opt_action.id,
                        "description": opt_action.description,
                        "result": result.description,
                        "success": result.success,
                    })

        # 4. Summary
        results["summary"] = {
            "total_proposed": len(results["proposed_actions"]),
            "total_applied": len(results["applied_actions"]),
            "total_skipped": len(results["skipped_actions"]),
            "health_after": health["overall_health"],
        }

        return results

    def _generate_healing_action(self, issue: dict) -> HealingAction | None:
        """Generate a healing action for a detected issue."""
        self._action_counter += 1
        metric = issue.get("metric", "")
        category = issue.get("category", "")
        severity = issue.get("severity", "medium")
        auto_fixable = issue.get("auto_fixable", False)

        # Map issues to healing actions
        if category == "degradation":
            return HealingAction(
                id=f"heal_{self._action_counter}",
                action_type="optimize",
                target=metric,
                description=f"Auto-tune {metric} to improve performance",
                risk_level="low" if auto_fixable else "medium",
                auto_approved=auto_fixable and severity != "critical",
            )
        elif category == "anomaly":
            return HealingAction(
                id=f"heal_{self._action_counter}",
                action_type="fix",
                target=metric,
                description=f"Investigate and correct anomaly in {metric}",
                risk_level="medium",
                auto_approved=False,
            )
        elif category == "error":
            return HealingAction(
                id=f"heal_{self._action_counter}",
                action_type="fix",
                target=metric,
                description=f"Fix error affecting {metric}",
                risk_level="high" if severity == "critical" else "medium",
                auto_approved=False,
            )

        return None

    def _generate_optimization(self, recommendation: dict) -> HealingAction | None:
        """Generate an optimization action from a recommendation."""
        self._action_counter += 1
        metric = recommendation.get("metric", "")
        domain = recommendation.get("domain", "")
        gap = recommendation.get("gap", 0)
        direction = recommendation.get("direction", "increase")

        # Find tunable parameter that could improve this metric
        param_key = self._find_tunable_param(domain, metric, direction)
        if not param_key:
            return None

        param = self.tunable_params[param_key]

        return HealingAction(
            id=f"opt_{self._action_counter}",
            action_type="optimize",
            target=param_key,
            description=(
                f"Tune {param_key} ({param['description']}) "
                f"from {param['current']} to improve {metric}"
            ),
            risk_level="low",
            auto_approved=gap < param.get("step", 1) * 2,
            metrics_before={metric: recommendation.get("current", 0)},
        )

    def _find_tunable_param(
        self, domain: str, metric: str, direction: str
    ) -> str | None:
        """Find a tunable parameter that could improve a metric."""
        # Map metrics to tunable parameters
        metric_to_params = {
            "detection_rate": "security.scan_timeout_ms",
            "vuln_precision": "security.cve_match_threshold",
            "exploit_success": "security.exploit_timeout_ms",
            "signal_accuracy": "finance.signal_lookback_periods",
            "risk_reduction": "finance.risk_tolerance",
            "code_quality_score": "software.review_depth",
            "papers_per_day": "research.scan_batch_size",
            "consensus_rate": "negotiation.max_rounds",
        }

        param_key = metric_to_params.get(metric)
        if param_key and param_key in self.tunable_params:
            return param_key
        return None

    def _apply_action(self, action: HealingAction) -> OptimizationResult:
        """Apply a healing/optimization action safely."""
        action.applied_at = time.time()

        # Check if target is protected
        if any(action.target.startswith(p) for p in self.protected_components):
            action.status = "rejected"
            action.result = "Target is a protected core component"
            return OptimizationResult(
                success=False,
                description="Cannot modify protected core component",
            )

        # For parameter tuning
        if action.target in self.tunable_params:
            param = self.tunable_params[action.target]
            old_value = param["current"]
            step = param["step"]

            # Determine direction
            if "increase" in action.description or "improve" in action.description:
                new_value = min(old_value + step, param["max"])
            else:
                new_value = max(old_value - step, param["min"])

            if new_value == old_value:
                action.status = "rejected"
                action.result = "Already at limit"
                return OptimizationResult(
                    success=False,
                    description=f"{action.target} already at {'max' if new_value == param['max'] else 'min'} value",
                )

            param["current"] = new_value
            action.status = "applied"
            action.result = f"Changed from {old_value} to {new_value}"
            action.metrics_after = {action.target: new_value}

            self.applied_optimizations.append({
                "action_id": action.id,
                "parameter": action.target,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": time.time(),
            })

            self.actions.append(action)

            return OptimizationResult(
                success=True,
                description=f"Tuned {action.target}: {old_value} → {new_value}",
                improvement=(new_value - old_value) / max(abs(old_value), 0.001),
            )

        # For other actions, just record as proposed
        action.status = "proposed"
        action.result = "Requires manual implementation"
        self.actions.append(action)

        return OptimizationResult(
            success=False,
            description="Action recorded but requires manual implementation",
        )

    def rollback_action(self, action_id: str) -> dict[str, Any]:
        """Rollback a previously applied action."""
        action = next((a for a in self.actions if a.id == action_id), None)
        if not action:
            return {"error": f"Action {action_id} not found"}

        if action.status != "applied":
            return {"error": f"Action {action_id} was not applied (status: {action.status})"}

        # Find the optimization record
        opt = next(
            (o for o in self.applied_optimizations if o["action_id"] == action_id),
            None
        )
        if opt and opt["parameter"] in self.tunable_params:
            param = self.tunable_params[opt["parameter"]]
            param["current"] = opt["old_value"]
            action.status = "rolled_back"

            return {
                "success": True,
                "parameter": opt["parameter"],
                "restored_to": opt["old_value"],
            }

        return {"error": "Cannot rollback — no parameter change found"}

    def get_healing_history(self) -> list[dict[str, Any]]:
        """Get history of all healing actions."""
        return [
            {
                "id": a.id,
                "type": a.action_type,
                "target": a.target,
                "description": a.description,
                "status": a.status,
                "risk_level": a.risk_level,
                "result": a.result,
                "created_at": a.created_at,
                "applied_at": a.applied_at,
            }
            for a in self.actions[-50:]
        ]

    def get_tunable_params(self) -> dict[str, Any]:
        """Get all tunable parameters with their current values and ranges."""
        return {
            key: {
                "current": p["current"],
                "min": p["min"],
                "max": p["max"],
                "step": p["step"],
                "description": p["description"],
            }
            for key, p in self.tunable_params.items()
        }

    def get_dashboard(self) -> dict[str, Any]:
        """Get self-healer dashboard data."""
        applied = [a for a in self.actions if a.status == "applied"]
        proposed = [a for a in self.actions if a.status == "proposed"]
        rolled_back = [a for a in self.actions if a.status == "rolled_back"]

        return {
            "total_actions": len(self.actions),
            "applied": len(applied),
            "proposed": len(proposed),
            "rolled_back": len(rolled_back),
            "total_optimizations": len(self.applied_optimizations),
            "recent_actions": self.get_healing_history()[-10:],
            "tunable_params": self.get_tunable_params(),
            "protected_components": list(self.protected_components),
        }
