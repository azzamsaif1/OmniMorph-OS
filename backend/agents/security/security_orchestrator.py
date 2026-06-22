"""Security orchestrator — LangGraph workflow: Recon → Analyze → Exploit → Report."""

import json
from typing import Any

from backend.agents.security.recon_agent import scan_common_ports, grab_banner
from backend.agents.security.vuln_analyzer import analyze_service, correlate_scan, calculate_risk_score
from backend.agents.security.exploit_agent import simulate_exploit, generate_remediation_report


class SecurityOrchestrator:
    """Orchestrates the full penetration testing pipeline (safe mode).

    Workflow: Reconnaissance → Vulnerability Analysis → Exploit Simulation → Report
    """

    def __init__(self):
        self.results: dict[str, Any] = {}
        self.evolution_history: list[dict] = []

    async def run_full_assessment(self, target_ip: str) -> dict[str, Any]:
        """Execute complete security assessment pipeline."""
        # Stage 1: Reconnaissance
        recon_results = self._recon(target_ip)
        self.results["reconnaissance"] = recon_results

        # Stage 2: Vulnerability Analysis
        vuln_results = self._analyze(recon_results)
        self.results["vulnerabilities"] = vuln_results

        # Stage 3: Exploit Simulation
        exploit_results = self._simulate_exploits(vuln_results, target_ip)
        self.results["exploit_simulation"] = exploit_results

        # Stage 4: Generate Report
        report = self._generate_report(recon_results, vuln_results, exploit_results)
        self.results["report"] = report

        # Stage 5: Self-evolution — learn from this assessment
        self._evolve(report)

        return self.results

    def _recon(self, target_ip: str) -> dict[str, Any]:
        """Stage 1: Network reconnaissance."""
        scan = scan_common_ports(target_ip)

        # Grab banners for open ports
        banners = {}
        for port_info in scan.get("ports", []):
            port = port_info["port"]
            banner = grab_banner(target_ip, port)
            if banner:
                banners[port] = banner

        scan["banners"] = banners
        return scan

    def _analyze(self, recon_results: dict) -> dict[str, Any]:
        """Stage 2: Vulnerability analysis."""
        all_vulns = []

        for port_info in recon_results.get("ports", []):
            service = port_info.get("service", "unknown")
            port = port_info["port"]
            banner = recon_results.get("banners", {}).get(str(port), "")

            service_vulns = analyze_service(service, banner, port)
            if service_vulns.get("vulnerabilities_found", 0) > 0:
                all_vulns.append(service_vulns)

        # Correlate with CVE database
        correlation = correlate_scan(recon_results)

        # Calculate risk score
        critical = sum(
            1 for v in correlation.get("vulnerabilities", [])
            if v.get("severity") == "critical"
        )
        high = sum(
            1 for v in correlation.get("vulnerabilities", [])
            if v.get("severity") == "high"
        )
        medium = sum(
            1 for v in correlation.get("vulnerabilities", [])
            if v.get("severity") == "medium"
        )
        open_ports = recon_results.get("open_ports_count", 0)

        risk_score = calculate_risk_score(open_ports, critical, high, medium)

        return {
            "service_analysis": all_vulns,
            "cve_correlation": correlation,
            "risk_score": risk_score,
            "summary": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "total": critical + high + medium,
            },
        }

    def _simulate_exploits(self, vuln_results: dict, target_ip: str) -> list[dict]:
        """Stage 3: Simulate exploitation of found vulnerabilities."""
        simulations = []
        vulns = vuln_results.get("cve_correlation", {}).get("vulnerabilities", [])

        for vuln in vulns:
            if vuln.get("exploitable"):
                result = simulate_exploit(
                    vuln["cve_id"], target_ip, vuln.get("port", 0)
                )
                simulations.append(result)

        return simulations

    def _generate_report(
        self, recon: dict, vulns: dict, exploits: list[dict]
    ) -> dict[str, Any]:
        """Stage 4: Generate comprehensive report."""
        all_vuln_list = vulns.get("cve_correlation", {}).get("vulnerabilities", [])
        remediation = generate_remediation_report(all_vuln_list)

        return {
            "target": recon.get("target", "unknown"),
            "open_ports": recon.get("open_ports_count", 0),
            "total_vulnerabilities": vulns.get("summary", {}).get("total", 0),
            "critical_vulnerabilities": vulns.get("summary", {}).get("critical", 0),
            "exploitable_count": len(exploits),
            "risk_score": vulns.get("risk_score", 0.0),
            "remediation": remediation,
            "executive_summary": self._build_executive_summary(recon, vulns, exploits),
        }

    def _build_executive_summary(
        self, recon: dict, vulns: dict, exploits: list[dict]
    ) -> str:
        """Build human-readable executive summary."""
        target = recon.get("target", "unknown")
        ports = recon.get("open_ports_count", 0)
        total_v = vulns.get("summary", {}).get("total", 0)
        critical = vulns.get("summary", {}).get("critical", 0)
        exploitable = len(exploits)

        return (
            f"Security assessment of {target}: "
            f"{ports} open ports discovered, "
            f"{total_v} vulnerabilities identified ({critical} critical), "
            f"{exploitable} confirmed exploitable. "
            f"Immediate remediation recommended for critical findings."
        )

    def _evolve(self, report: dict) -> None:
        """Stage 5: Self-evolution — record learnings for future assessments."""
        learning = {
            "assessment_target": report.get("target"),
            "findings_count": report.get("total_vulnerabilities", 0),
            "new_patterns": [],
            "strategy_updates": [],
        }

        # Learn from exploitable findings
        if report.get("exploitable_count", 0) > 0:
            learning["strategy_updates"].append(
                "Prioritize service enumeration for targets with multiple open ports"
            )

        if report.get("critical_vulnerabilities", 0) > 2:
            learning["strategy_updates"].append(
                "Target likely unpatched — expand scan to full port range"
            )

        self.evolution_history.append(learning)
