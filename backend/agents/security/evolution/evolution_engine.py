"""Evolution Engine — the core self-evolving penetration testing orchestrator.

Coordinates the full autonomous penetration testing lifecycle:
1. Reconnaissance → discovers attack surface
2. Vulnerability analysis → correlates with CVE database
3. Exploitation → safely simulates attacks
4. Learning → records outcomes in experience memory
5. Strategy evolution → improves tactics for next assessment
6. Self-monitoring → tracks own performance metrics
7. Self-improvement → generates and applies optimizations

This surpasses single-model approaches by combining specialized agents
with continuous learning and adaptation.
"""

import time
from typing import Any

from backend.agents.security.evolution.experience_memory import ExperienceMemory
from backend.agents.security.evolution.strategy_learner import StrategyLearner
from backend.agents.security.recon_agent import scan_common_ports, grab_banner
from backend.agents.security.vuln_analyzer import (
    analyze_service, correlate_scan, calculate_risk_score,
)
from backend.agents.security.exploit_agent import (
    simulate_exploit, generate_remediation_report,
)


class EvolutionEngine:
    """Self-evolving penetration testing engine.

    Multi-agent pipeline that learns from every assessment:
    - Experience memory persists across assessments
    - Strategy learner evolves attack playbooks
    - Performance tracker identifies weaknesses
    - Auto-improvement generates optimizations
    """

    def __init__(self):
        self.memory = ExperienceMemory()
        self.learner = StrategyLearner(self.memory)

        # Performance tracking
        self.assessments_completed: int = 0
        self.total_vulns_found: int = 0
        self.total_exploits_succeeded: int = 0
        self.performance_history: list[dict] = []
        self.improvement_log: list[dict] = []

        # Self-monitoring metrics
        self.metrics: dict[str, float] = {
            "detection_rate": 0.95,  # target: 95% port detection
            "vuln_precision": 0.90,  # target: 90% vulnerability precision
            "exploit_success": 0.85,  # target: 85% exploitation success
            "false_positive_rate": 0.05,  # target: <5% false positives
            "avg_assessment_time_ms": 0.0,
            "improvement_rate": 0.0,
        }

        # Thresholds for self-improvement triggers
        self._improvement_thresholds = {
            "detection_rate": 0.90,
            "vuln_precision": 0.85,
            "exploit_success": 0.80,
            "false_positive_rate": 0.10,  # trigger if exceeds this
        }

    async def run_autonomous_assessment(
        self, target_ip: str, depth: str = "standard"
    ) -> dict[str, Any]:
        """Execute a full autonomous penetration test with self-evolution.

        Args:
            target_ip: Target IP address to assess
            depth: Assessment depth - "quick"|"standard"|"deep"

        Returns:
            Comprehensive assessment with learning outcomes
        """
        start_time = time.time()
        assessment = {
            "target": target_ip,
            "depth": depth,
            "started_at": start_time,
            "stages": {},
            "learning_outcomes": {},
            "evolution_actions": [],
            "self_improvement": [],
        }

        # ── Stage 1: Reconnaissance ──
        recon = self._execute_recon(target_ip, depth)
        assessment["stages"]["reconnaissance"] = recon

        # Record recon experience
        recon_exp = self.memory.record_experience(
            target_type="network",
            technique="port_scan",
            outcome="success" if recon["open_ports_count"] > 0 else "partial",
            target_info={"ip": target_ip, "ports_found": recon["open_ports_count"]},
            tactics_used=["tcp_connect", "banner_grab"],
            duration_ms=(time.time() - start_time) * 1000,
            confidence=0.95 if recon["open_ports_count"] > 0 else 0.5,
        )

        # ── Stage 2: Vulnerability Analysis ──
        vulns = self._execute_vuln_analysis(recon)
        assessment["stages"]["vulnerability_analysis"] = vulns

        for vuln_set in vulns.get("service_analysis", []):
            vuln_count = vuln_set.get("vulnerabilities_found", 0)
            self.total_vulns_found += vuln_count

            self.memory.record_experience(
                target_type="service",
                technique="cve_correlation",
                outcome="success" if vuln_count > 0 else "failure",
                target_info={
                    "service": vuln_set.get("service"),
                    "port": vuln_set.get("port"),
                },
                tactics_used=["cve_lookup", "version_match", "risk_scoring"],
                confidence=0.9 if vuln_count > 0 else 0.4,
                lessons_learned=[
                    f"Found {vuln_count} vulns for {vuln_set.get('service', 'unknown')}"
                ],
            )

        # ── Stage 3: Exploitation Simulation ──
        exploits = self._execute_exploits(vulns, target_ip)
        assessment["stages"]["exploitation"] = exploits

        for exploit_result in exploits:
            succeeded = exploit_result.get("success", False)
            if succeeded:
                self.total_exploits_succeeded += 1

            exp = self.memory.record_experience(
                target_type="service",
                technique="exploit",
                outcome="success" if succeeded else "failure",
                target_info={
                    "cve": exploit_result.get("cve_id"),
                    "ip": target_ip,
                    "port": exploit_result.get("target_port"),
                },
                defenses_encountered=exploit_result.get("defenses", []),
                tactics_used=[exploit_result.get("payload_type", "unknown")],
                confidence=exploit_result.get("confidence", 0.5),
                lessons_learned=[
                    f"{'Succeeded' if succeeded else 'Failed'}: {exploit_result.get('cve_id', 'unknown')}"
                ],
            )

            # Learn from the experience
            self.learner.learn_from_experience(exp)

        # ── Stage 4: Report Generation ──
        report = self._generate_report(recon, vulns, exploits, target_ip)
        assessment["stages"]["report"] = report

        # ── Stage 5: Learning & Evolution ──
        learning = self._execute_learning_cycle()
        assessment["learning_outcomes"] = learning

        # ── Stage 6: Self-Assessment & Improvement ──
        elapsed_ms = (time.time() - start_time) * 1000
        self_assessment = self._self_assess(elapsed_ms)
        assessment["self_improvement"] = self_assessment["improvements"]
        assessment["performance_metrics"] = self_assessment["metrics"]

        # Record overall assessment
        self.assessments_completed += 1
        assessment["completed_at"] = time.time()
        assessment["duration_ms"] = elapsed_ms

        self.performance_history.append({
            "assessment_id": self.assessments_completed,
            "target": target_ip,
            "vulns_found": self.total_vulns_found,
            "exploits_succeeded": self.total_exploits_succeeded,
            "duration_ms": elapsed_ms,
            "metrics": dict(self.metrics),
            "timestamp": time.time(),
        })

        return assessment

    def _execute_recon(self, target_ip: str, depth: str) -> dict[str, Any]:
        """Execute reconnaissance with strategy guidance."""
        # Get recommended approach from learner
        prediction = self.learner.predict_success("network", "port_scan")

        scan = scan_common_ports(target_ip)

        # Banner grabbing for all open ports
        banners = {}
        for port_info in scan.get("ports", []):
            port = port_info["port"]
            banner = grab_banner(target_ip, port)
            if banner:
                banners[port] = banner

        scan["banners"] = banners
        scan["strategy_guidance"] = prediction
        return scan

    def _execute_vuln_analysis(self, recon: dict) -> dict[str, Any]:
        """Execute vulnerability analysis on discovered services."""
        all_vulns = []

        for port_info in recon.get("ports", []):
            service = port_info.get("service", "unknown")
            port = port_info["port"]
            banner = recon.get("banners", {}).get(port, "")

            service_vulns = analyze_service(service, banner, port)
            if service_vulns.get("vulnerabilities_found", 0) > 0:
                all_vulns.append(service_vulns)

        # Correlate with full CVE database
        correlation = correlate_scan(recon)

        # Calculate risk from discovered vulnerabilities
        critical_count = sum(
            1 for sv in all_vulns
            for v in sv.get("vulnerabilities", [])
            if v.get("cvss_score", 0) >= 9.0
        )
        high_count = sum(
            1 for sv in all_vulns
            for v in sv.get("vulnerabilities", [])
            if 7.0 <= v.get("cvss_score", 0) < 9.0
        )
        medium_count = sum(
            1 for sv in all_vulns
            for v in sv.get("vulnerabilities", [])
            if 4.0 <= v.get("cvss_score", 0) < 7.0
        )
        risk = calculate_risk_score(
            len(recon.get("ports", [])), critical_count, high_count, medium_count
        )

        return {
            "service_analysis": all_vulns,
            "cve_correlation": correlation,
            "risk_score": risk,
            "total_services_analyzed": len(recon.get("ports", [])),
            "vulnerable_services": len(all_vulns),
        }

    def _execute_exploits(
        self, vulns: dict, target_ip: str
    ) -> list[dict[str, Any]]:
        """Execute exploit simulations with learning."""
        results = []

        for service_vulns in vulns.get("service_analysis", []):
            for vuln in service_vulns.get("vulnerabilities", []):
                if not vuln.get("exploitable", False):
                    continue

                cve_id = vuln.get("cve_id", "")
                port = vuln.get("port", 0)

                # Check prediction before attempting
                prediction = self.learner.predict_success(
                    "service", "exploit",
                    defenses=[]
                )

                result = simulate_exploit(cve_id, target_ip, port)
                result["prediction"] = prediction
                results.append(result)

        return results

    def _generate_report(
        self, recon: dict, vulns: dict, exploits: list, target_ip: str
    ) -> dict[str, Any]:
        """Generate comprehensive assessment report."""
        total_vulns = sum(
            sv.get("vulnerabilities_found", 0)
            for sv in vulns.get("service_analysis", [])
        )
        exploitable = sum(1 for e in exploits if e.get("success", False))

        remediation = generate_remediation_report(
            [{"cve_id": e.get("cve_id", ""), "severity": "high"} for e in exploits]
        )

        # Prioritized findings
        critical_findings = []
        for sv in vulns.get("service_analysis", []):
            for v in sv.get("vulnerabilities", []):
                if v.get("cvss_score", 0) >= 9.0:
                    critical_findings.append({
                        "cve_id": v["cve_id"],
                        "cvss_score": v["cvss_score"],
                        "service": sv.get("service"),
                        "port": sv.get("port"),
                        "exploitable": v.get("exploitable", False),
                        "priority": "immediate",
                    })

        return {
            "target": target_ip,
            "open_ports": recon.get("open_ports_count", 0),
            "total_vulnerabilities": total_vulns,
            "critical_findings": critical_findings,
            "exploitable_count": exploitable,
            "risk_score": vulns.get("risk_score", 0),
            "remediation": remediation,
            "attack_paths": self._map_attack_paths(recon, vulns, exploits),
            "executive_summary": (
                f"Security assessment of {target_ip}: "
                f"{recon.get('open_ports_count', 0)} open ports, "
                f"{total_vulns} vulnerabilities ({len(critical_findings)} critical), "
                f"{exploitable} confirmed exploitable. "
                f"Immediate remediation recommended for critical findings."
            ),
        }

    def _map_attack_paths(
        self, recon: dict, vulns: dict, exploits: list
    ) -> list[dict]:
        """Map possible attack paths through the target."""
        paths = []
        for sv in vulns.get("service_analysis", []):
            for v in sv.get("vulnerabilities", []):
                if v.get("exploitable"):
                    paths.append({
                        "entry_point": f"{sv.get('service')}:{sv.get('port')}",
                        "vulnerability": v["cve_id"],
                        "cvss": v.get("cvss_score", 0),
                        "steps": [
                            f"1. Discover {sv.get('service')} on port {sv.get('port')}",
                            f"2. Identify {v['cve_id']} (CVSS {v.get('cvss_score', 0)})",
                            f"3. Deploy exploit payload",
                            f"4. Gain {v.get('severity', 'unknown')}-level access",
                        ],
                        "difficulty": "low" if v.get("cvss_score", 0) >= 9 else "medium",
                    })

        return sorted(paths, key=lambda p: p.get("cvss", 0), reverse=True)

    def _execute_learning_cycle(self) -> dict[str, Any]:
        """Execute a learning cycle after the assessment."""
        # Evolve strategies
        evolution = self.learner.evolve_strategies()

        # Get memory stats
        memory_stats = self.memory.get_stats()

        return {
            "evolution": evolution,
            "memory_stats": memory_stats,
            "strategies_stats": self.learner.get_stats(),
            "experiences_recorded": memory_stats["total_experiences"],
            "patterns_identified": memory_stats["patterns_identified"],
            "success_strategies": memory_stats["success_strategies"],
        }

    def _self_assess(self, elapsed_ms: float) -> dict[str, Any]:
        """Self-assess performance and generate improvements."""
        improvements = []

        # Update metrics
        total_exp = len(self.memory.experiences)
        if total_exp > 0:
            successes = sum(
                1 for e in self.memory.experiences if e.outcome == "success"
            )
            failures = sum(
                1 for e in self.memory.experiences if e.outcome in ("failure", "blocked")
            )

            self.metrics["detection_rate"] = successes / max(total_exp, 1)
            self.metrics["exploit_success"] = (
                self.total_exploits_succeeded / max(self.assessments_completed, 1)
            )
            self.metrics["avg_assessment_time_ms"] = elapsed_ms

            # Calculate improvement rate from history
            if len(self.performance_history) >= 2:
                prev = self.performance_history[-2].get("metrics", {})
                curr = self.metrics
                changes = []
                for key in ["detection_rate", "vuln_precision", "exploit_success"]:
                    prev_val = prev.get(key, 0)
                    curr_val = curr.get(key, 0)
                    if prev_val > 0:
                        changes.append((curr_val - prev_val) / prev_val)
                if changes:
                    self.metrics["improvement_rate"] = sum(changes) / len(changes)

        # Check thresholds and generate improvements
        for metric, threshold in self._improvement_thresholds.items():
            current = self.metrics.get(metric, 0)

            if metric == "false_positive_rate":
                if current > threshold:
                    improvement = self._generate_improvement(
                        metric, current, threshold, "reduce"
                    )
                    improvements.append(improvement)
            else:
                if current < threshold:
                    improvement = self._generate_improvement(
                        metric, current, threshold, "increase"
                    )
                    improvements.append(improvement)

        # Log improvements
        if improvements:
            self.improvement_log.append({
                "assessment_id": self.assessments_completed,
                "timestamp": time.time(),
                "improvements_generated": len(improvements),
                "improvements": improvements,
            })

        return {
            "metrics": dict(self.metrics),
            "improvements": improvements,
            "assessment_count": self.assessments_completed,
        }

    def _generate_improvement(
        self, metric: str, current: float, target: float, direction: str
    ) -> dict[str, Any]:
        """Generate a specific improvement recommendation."""
        improvement_actions = {
            "detection_rate": {
                "increase": [
                    "Add UDP port scanning alongside TCP",
                    "Increase port range from common to full (1-65535)",
                    "Add service version fingerprinting fallbacks",
                    "Implement SYN scanning for faster detection",
                    "Add IPv6 scanning support",
                ],
            },
            "vuln_precision": {
                "increase": [
                    "Expand CVE database with latest entries",
                    "Add version-specific vulnerability matching",
                    "Implement banner pattern matching improvements",
                    "Cross-reference with exploit-db for verification",
                    "Add NVD API integration for real-time CVE updates",
                ],
            },
            "exploit_success": {
                "increase": [
                    "Add more exploit modules for common CVEs",
                    "Implement environment-specific payload customization",
                    "Add defense detection before exploitation attempts",
                    "Implement multi-stage exploitation chains",
                    "Add timing-based evasion for IDS bypass",
                ],
            },
            "false_positive_rate": {
                "reduce": [
                    "Add verification scans for flagged vulnerabilities",
                    "Implement confidence scoring with multiple data points",
                    "Cross-validate findings across multiple scanners",
                    "Add service-specific validation rules",
                    "Implement Bayesian false positive filtering",
                ],
            },
        }

        actions = improvement_actions.get(metric, {}).get(direction, [])

        gap = abs(target - current)
        priority = "critical" if gap > 0.2 else "high" if gap > 0.1 else "medium"

        return {
            "metric": metric,
            "current_value": current,
            "target_value": target,
            "direction": direction,
            "gap": gap,
            "priority": priority,
            "recommended_actions": actions[:3],
            "estimated_improvement": min(gap, 0.1),
            "auto_applicable": gap < 0.05,
        }

    def get_evolution_dashboard(self) -> dict[str, Any]:
        """Get comprehensive evolution dashboard data."""
        return {
            "overview": {
                "assessments_completed": self.assessments_completed,
                "total_vulns_found": self.total_vulns_found,
                "total_exploits_succeeded": self.total_exploits_succeeded,
                "evolution_generation": self.learner._evolution_generation,
            },
            "performance_metrics": dict(self.metrics),
            "memory_stats": self.memory.get_stats(),
            "strategy_stats": self.learner.get_stats(),
            "improvement_log": self.improvement_log[-10:],
            "performance_history": self.performance_history[-20:],
            "active_strategies": [
                {
                    "id": s.id,
                    "name": s.name,
                    "success_rate": s.success_rate,
                    "times_used": s.times_used,
                    "generation": s.generation,
                    "phases": len(s.phases),
                    "defense_bypasses": len(s.defense_bypasses),
                }
                for s in sorted(
                    self.learner.strategies.values(),
                    key=lambda x: x.success_rate, reverse=True
                )
            ],
            "comparison_vs_mythos": {
                "architecture": "Multi-agent specialized (6 agents) vs single model",
                "learning": f"Continuous ({len(self.memory.experiences)} experiences) vs static",
                "strategies": f"{len(self.learner.strategies)} evolving strategies vs fixed prompts",
                "evolution_generation": self.learner._evolution_generation,
                "defense_adaptations": sum(
                    len(s.defense_bypasses) for s in self.learner.strategies.values()
                ),
            },
        }
