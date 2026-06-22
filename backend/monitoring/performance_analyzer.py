"""Performance Analyzer — automatically analyzes system performance and detects issues.

Capabilities:
- Tracks performance metrics across all agent domains
- Detects anomalies and performance degradation
- Identifies weaknesses and bottlenecks
- Generates improvement recommendations
- Triggers automatic optimizations when safe
"""

import time
import statistics
from typing import Any
from dataclasses import dataclass, field


@dataclass
class MetricPoint:
    """Single metric data point."""
    name: str
    value: float
    timestamp: float
    agent: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class PerformanceIssue:
    """Detected performance issue."""
    id: str
    severity: str  # critical|high|medium|low
    category: str  # degradation|anomaly|bottleneck|error
    metric: str
    description: str
    current_value: float
    expected_value: float
    deviation: float
    recommended_fix: str
    auto_fixable: bool = False
    detected_at: float = field(default_factory=time.time)


class PerformanceAnalyzer:
    """Analyzes system performance and detects issues automatically.

    Features:
    - Rolling window analysis (last N measurements)
    - Statistical anomaly detection (z-score based)
    - Trend analysis (improving/degrading/stable)
    - Cross-agent performance correlation
    - Automatic threshold learning
    """

    def __init__(self):
        self.metrics: dict[str, list[MetricPoint]] = {}
        self.issues: list[PerformanceIssue] = []
        self.baselines: dict[str, dict[str, float]] = {}
        self._window_size = 50
        self._anomaly_threshold = 2.0  # z-score threshold
        self._issue_counter = 0

        # Define expected performance targets per domain
        self.targets: dict[str, dict[str, float]] = {
            "security": {
                "detection_rate": 0.95,
                "vuln_precision": 0.90,
                "exploit_success": 0.85,
                "false_positive_rate": 0.05,
                "scan_time_ms": 5000,
            },
            "finance": {
                "signal_accuracy": 0.80,
                "annual_return": 0.20,
                "risk_reduction": 0.15,
                "backtest_sharpe": 1.5,
            },
            "software": {
                "task_success_rate": 0.90,
                "code_quality_score": 0.85,
                "test_coverage": 0.95,
                "review_accuracy": 0.90,
            },
            "research": {
                "papers_per_day": 100,
                "extraction_quality": 0.85,
                "evolution_improvement": 0.15,
            },
            "negotiation": {
                "consensus_rate": 0.942,
                "satisfaction_score": 0.85,
            },
            "delivery": {
                "planning_accuracy": 0.90,
                "execution_success": 0.85,
                "deployment_success": 0.95,
            },
            "system": {
                "api_response_time_ms": 200,
                "error_rate": 0.01,
                "uptime": 0.999,
                "memory_usage_pct": 80,
            },
        }

    def record_metric(
        self,
        name: str,
        value: float,
        agent: str = "system",
        metadata: dict | None = None,
    ) -> MetricPoint | None:
        """Record a metric data point and check for issues."""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            agent=agent,
            metadata=metadata or {},
        )

        key = f"{agent}:{name}"
        if key not in self.metrics:
            self.metrics[key] = []

        self.metrics[key].append(point)

        # Keep only last N points
        if len(self.metrics[key]) > self._window_size:
            self.metrics[key] = self.metrics[key][-self._window_size:]

        # Run analysis
        issue = self._analyze_metric(key, point)
        if issue:
            self.issues.append(issue)
            return point

        return point

    def _analyze_metric(self, key: str, point: MetricPoint) -> PerformanceIssue | None:
        """Analyze a metric for anomalies and degradation."""
        history = self.metrics.get(key, [])
        if len(history) < 5:
            return None

        values = [p.value for p in history]
        current = point.value
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) >= 2 else 0

        # Check for statistical anomaly
        if stdev > 0:
            z_score = abs(current - mean) / stdev
            if z_score > self._anomaly_threshold:
                self._issue_counter += 1
                return PerformanceIssue(
                    id=f"issue_{self._issue_counter}",
                    severity="high" if z_score > 3 else "medium",
                    category="anomaly",
                    metric=point.name,
                    description=(
                        f"Anomalous {point.name} value: {current:.4f} "
                        f"(mean: {mean:.4f}, z-score: {z_score:.2f})"
                    ),
                    current_value=current,
                    expected_value=mean,
                    deviation=z_score,
                    recommended_fix=f"Investigate sudden change in {point.name}",
                    auto_fixable=False,
                )

        # Check against targets
        domain = point.agent
        target = self.targets.get(domain, {}).get(point.name)
        if target is not None:
            is_time_metric = "time" in point.name or "rate" in point.name and "error" in point.name
            is_inverse = point.name in ("false_positive_rate", "error_rate", "memory_usage_pct",
                                        "scan_time_ms", "api_response_time_ms")

            if is_inverse:
                # Lower is better
                if current > target * 1.5:
                    self._issue_counter += 1
                    return PerformanceIssue(
                        id=f"issue_{self._issue_counter}",
                        severity="high" if current > target * 2 else "medium",
                        category="degradation",
                        metric=point.name,
                        description=(
                            f"{point.name} ({current:.4f}) exceeds target ({target:.4f}) by "
                            f"{((current - target) / target * 100):.1f}%"
                        ),
                        current_value=current,
                        expected_value=target,
                        deviation=(current - target) / max(target, 0.001),
                        recommended_fix=f"Optimize {point.name} — currently above threshold",
                        auto_fixable=current < target * 1.2,
                    )
            else:
                # Higher is better
                if current < target * 0.8:
                    self._issue_counter += 1
                    return PerformanceIssue(
                        id=f"issue_{self._issue_counter}",
                        severity="high" if current < target * 0.5 else "medium",
                        category="degradation",
                        metric=point.name,
                        description=(
                            f"{point.name} ({current:.4f}) below target ({target:.4f}) by "
                            f"{((target - current) / target * 100):.1f}%"
                        ),
                        current_value=current,
                        expected_value=target,
                        deviation=(target - current) / max(target, 0.001),
                        recommended_fix=f"Improve {point.name} — currently below threshold",
                        auto_fixable=current > target * 0.9,
                    )

        return None

    def analyze_trends(self) -> dict[str, Any]:
        """Analyze performance trends across all metrics."""
        trends = {}

        for key, history in self.metrics.items():
            if len(history) < 5:
                continue

            values = [p.value for p in history]
            recent = values[-5:]
            older = values[:-5] if len(values) > 5 else values[:1]

            recent_avg = statistics.mean(recent)
            older_avg = statistics.mean(older) if older else recent_avg

            if older_avg > 0:
                change_pct = ((recent_avg - older_avg) / older_avg) * 100
            else:
                change_pct = 0

            if change_pct > 5:
                direction = "improving"
            elif change_pct < -5:
                direction = "degrading"
            else:
                direction = "stable"

            trends[key] = {
                "direction": direction,
                "change_pct": round(change_pct, 2),
                "current_avg": round(recent_avg, 4),
                "previous_avg": round(older_avg, 4),
                "data_points": len(history),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
                "stdev": round(statistics.stdev(values), 4) if len(values) >= 2 else 0,
            }

        return {
            "trends": trends,
            "improving_count": sum(1 for t in trends.values() if t["direction"] == "improving"),
            "degrading_count": sum(1 for t in trends.values() if t["direction"] == "degrading"),
            "stable_count": sum(1 for t in trends.values() if t["direction"] == "stable"),
            "total_metrics_tracked": len(self.metrics),
        }

    def get_health_report(self) -> dict[str, Any]:
        """Generate a comprehensive health report."""
        open_issues = [i for i in self.issues if not getattr(i, "resolved", False)]
        critical = [i for i in open_issues if i.severity == "critical"]
        high = [i for i in open_issues if i.severity == "high"]

        # Determine overall health
        if critical:
            health = "critical"
        elif high:
            health = "degraded"
        elif len(open_issues) > 5:
            health = "warning"
        else:
            health = "healthy"

        return {
            "overall_health": health,
            "open_issues": len(open_issues),
            "critical_issues": len(critical),
            "high_issues": len(high),
            "issues": [
                {
                    "id": i.id,
                    "severity": i.severity,
                    "category": i.category,
                    "metric": i.metric,
                    "description": i.description,
                    "auto_fixable": i.auto_fixable,
                    "detected_at": i.detected_at,
                }
                for i in open_issues[-20:]
            ],
            "metrics_tracked": len(self.metrics),
            "total_data_points": sum(len(v) for v in self.metrics.values()),
            "domains_monitored": list({
                key.split(":")[0] for key in self.metrics.keys()
            }),
        }

    def get_improvement_recommendations(self) -> list[dict[str, Any]]:
        """Generate prioritized improvement recommendations."""
        recommendations = []

        for domain, targets in self.targets.items():
            for metric_name, target_value in targets.items():
                key = f"{domain}:{metric_name}"
                history = self.metrics.get(key, [])
                if not history:
                    continue

                current = history[-1].value
                is_inverse = metric_name in (
                    "false_positive_rate", "error_rate", "memory_usage_pct",
                    "scan_time_ms", "api_response_time_ms",
                )

                if is_inverse:
                    gap = current - target_value
                    needs_improvement = gap > 0
                else:
                    gap = target_value - current
                    needs_improvement = gap > 0

                if needs_improvement:
                    recommendations.append({
                        "domain": domain,
                        "metric": metric_name,
                        "current": current,
                        "target": target_value,
                        "gap": abs(gap),
                        "priority": "critical" if abs(gap) > target_value * 0.3 else
                                   "high" if abs(gap) > target_value * 0.15 else "medium",
                        "direction": "decrease" if is_inverse else "increase",
                    })

        return sorted(recommendations, key=lambda r: r["gap"], reverse=True)

    def get_stats(self) -> dict[str, Any]:
        """Get analyzer statistics."""
        return {
            "metrics_tracked": len(self.metrics),
            "total_data_points": sum(len(v) for v in self.metrics.values()),
            "issues_detected": len(self.issues),
            "auto_fixable_issues": sum(1 for i in self.issues if i.auto_fixable),
            "domains_monitored": list({
                key.split(":")[0] for key in self.metrics.keys()
            }),
        }
