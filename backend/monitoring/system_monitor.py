"""System Monitor — real-time observability for all OmniMorph-OS agents.

Provides centralized monitoring with:
- Agent health tracking
- Request/response metrics
- Error rate monitoring
- Resource usage tracking
- Event timeline
- Real-time WebSocket updates
"""

import time
import os
from typing import Any
from dataclasses import dataclass, field
from collections import deque


@dataclass
class AgentHealthStatus:
    """Health status of a single agent."""
    agent_id: str
    domain: str
    status: str = "healthy"  # healthy|degraded|error|offline
    last_heartbeat: float = field(default_factory=time.time)
    requests_total: int = 0
    requests_failed: int = 0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    last_error: str = ""
    uptime_start: float = field(default_factory=time.time)


@dataclass
class SystemEvent:
    """System event for the timeline."""
    timestamp: float
    event_type: str  # info|warning|error|improvement|evolution
    source: str
    message: str
    metadata: dict = field(default_factory=dict)


class SystemMonitor:
    """Centralized monitoring for all OmniMorph-OS components.

    Features:
    - Agent health tracking with heartbeat monitoring
    - Request/response latency tracking
    - Error rate monitoring with alerting
    - System resource monitoring
    - Event timeline with filtering
    - Real-time metrics aggregation
    """

    def __init__(self):
        self.agents: dict[str, AgentHealthStatus] = {}
        self.events: deque[SystemEvent] = deque(maxlen=1000)
        self.request_log: deque[dict] = deque(maxlen=5000)
        self._start_time = time.time()

        # Initialize all known agents
        self._init_agents()

    def _init_agents(self) -> None:
        """Register all known agents for monitoring."""
        agent_registry = {
            # Core agents (Layer 0-1)
            "orchestrator": "core",
            "analysis_supervisor": "core",
            "interface_supervisor": "core",
            "execution_supervisor": "core",
            "memory_supervisor": "core",
            "oversight_supervisor": "core",
            # Security agents (Layer 2)
            "recon_agent": "security",
            "vuln_analyzer": "security",
            "exploit_agent": "security",
            "security_orchestrator": "security",
            "self_evolve": "security",
            "evolution_engine": "security",
            # Finance agents
            "trading_engine": "finance",
            "portfolio_manager": "finance",
            "finance_orchestrator": "finance",
            # Software agents
            "web_agent": "software",
            "systems_agent": "software",
            "security_code_agent": "software",
            "ai_agent": "software",
            "devops_agent": "software",
            "testing_agent": "software",
            "database_agent": "software",
            "frontend_agent": "software",
            "code_review_agent": "software",
            "software_orchestrator": "software",
            # Research agents
            "arxiv_scanner": "research",
            "knowledge_extractor": "research",
            "research_evolver": "research",
            # Business agents
            "market_analyst": "business",
            "sales_agent": "business",
            # Negotiation agents
            "diplomat_agent": "negotiation",
            "contract_agent": "negotiation",
            # Delivery agents
            "planner_agent": "delivery",
            "executor_agent": "delivery",
            "git_agent": "delivery",
            "docker_agent": "delivery",
            # Training
            "curriculum_generator": "training",
            "moe_router": "training",
            "trainer": "training",
        }

        for agent_id, domain in agent_registry.items():
            self.agents[agent_id] = AgentHealthStatus(
                agent_id=agent_id, domain=domain
            )

    def record_request(
        self,
        agent_id: str,
        endpoint: str,
        response_time_ms: float,
        status_code: int = 200,
        error: str = "",
    ) -> None:
        """Record an API request for monitoring."""
        self.request_log.append({
            "agent_id": agent_id,
            "endpoint": endpoint,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "error": error,
            "timestamp": time.time(),
        })

        # Update agent health
        agent = self.agents.get(agent_id)
        if agent:
            agent.requests_total += 1
            agent.last_heartbeat = time.time()

            if status_code >= 400 or error:
                agent.requests_failed += 1
                agent.last_error = error or f"HTTP {status_code}"

            agent.error_rate = agent.requests_failed / max(agent.requests_total, 1)

            # Update running average response time
            n = agent.requests_total
            agent.avg_response_time_ms = (
                (agent.avg_response_time_ms * (n - 1) + response_time_ms) / n
            )

            # Update status based on metrics
            if agent.error_rate > 0.5:
                agent.status = "error"
            elif agent.error_rate > 0.1 or agent.avg_response_time_ms > 5000:
                agent.status = "degraded"
            else:
                agent.status = "healthy"

    def record_event(
        self,
        event_type: str,
        source: str,
        message: str,
        metadata: dict | None = None,
    ) -> SystemEvent:
        """Record a system event."""
        event = SystemEvent(
            timestamp=time.time(),
            event_type=event_type,
            source=source,
            message=message,
            metadata=metadata or {},
        )
        self.events.append(event)
        return event

    def get_agent_health(self, agent_id: str | None = None) -> dict[str, Any]:
        """Get health status for one or all agents."""
        if agent_id:
            agent = self.agents.get(agent_id)
            if not agent:
                return {"error": f"Agent {agent_id} not found"}
            return {
                "agent_id": agent.agent_id,
                "domain": agent.domain,
                "status": agent.status,
                "last_heartbeat": agent.last_heartbeat,
                "requests_total": agent.requests_total,
                "requests_failed": agent.requests_failed,
                "error_rate": agent.error_rate,
                "avg_response_time_ms": agent.avg_response_time_ms,
                "last_error": agent.last_error,
                "uptime_seconds": time.time() - agent.uptime_start,
            }

        return {
            "agents": {
                aid: {
                    "domain": a.domain,
                    "status": a.status,
                    "requests_total": a.requests_total,
                    "error_rate": a.error_rate,
                    "avg_response_time_ms": round(a.avg_response_time_ms, 2),
                }
                for aid, a in self.agents.items()
            },
            "summary": self._get_health_summary(),
        }

    def _get_health_summary(self) -> dict[str, Any]:
        """Get overall health summary."""
        agents = list(self.agents.values())
        healthy = sum(1 for a in agents if a.status == "healthy")
        degraded = sum(1 for a in agents if a.status == "degraded")
        error = sum(1 for a in agents if a.status == "error")
        offline = sum(1 for a in agents if a.status == "offline")

        total_requests = sum(a.requests_total for a in agents)
        total_errors = sum(a.requests_failed for a in agents)

        return {
            "total_agents": len(agents),
            "healthy": healthy,
            "degraded": degraded,
            "error": error,
            "offline": offline,
            "overall_status": (
                "critical" if error > 0 else
                "degraded" if degraded > 0 else
                "healthy"
            ),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "global_error_rate": total_errors / max(total_requests, 1),
        }

    def get_domain_health(self) -> dict[str, Any]:
        """Get health aggregated by domain."""
        domains: dict[str, list[AgentHealthStatus]] = {}
        for agent in self.agents.values():
            if agent.domain not in domains:
                domains[agent.domain] = []
            domains[agent.domain].append(agent)

        return {
            domain: {
                "agents": len(agents),
                "healthy": sum(1 for a in agents if a.status == "healthy"),
                "total_requests": sum(a.requests_total for a in agents),
                "avg_response_time_ms": round(
                    sum(a.avg_response_time_ms for a in agents) / max(len(agents), 1), 2
                ),
                "error_rate": sum(a.requests_failed for a in agents) / max(
                    sum(a.requests_total for a in agents), 1
                ),
            }
            for domain, agents in domains.items()
        }

    def get_events(
        self,
        event_type: str | None = None,
        source: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get system events with optional filtering."""
        events = list(self.events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]

        events = events[-limit:]

        return [
            {
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "source": e.source,
                "message": e.message,
                "metadata": e.metadata,
            }
            for e in events
        ]

    def get_request_metrics(self, window_seconds: int = 300) -> dict[str, Any]:
        """Get request metrics for the last N seconds."""
        cutoff = time.time() - window_seconds
        recent = [r for r in self.request_log if r["timestamp"] > cutoff]

        if not recent:
            return {
                "window_seconds": window_seconds,
                "total_requests": 0,
                "requests_per_second": 0,
            }

        response_times = [r["response_time_ms"] for r in recent]
        errors = [r for r in recent if r["status_code"] >= 400 or r["error"]]

        # Group by endpoint
        by_endpoint: dict[str, list[dict]] = {}
        for r in recent:
            ep = r["endpoint"]
            if ep not in by_endpoint:
                by_endpoint[ep] = []
            by_endpoint[ep].append(r)

        return {
            "window_seconds": window_seconds,
            "total_requests": len(recent),
            "requests_per_second": round(len(recent) / window_seconds, 2),
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
            "p50_response_time_ms": round(sorted(response_times)[len(response_times) // 2], 2),
            "p95_response_time_ms": round(
                sorted(response_times)[int(len(response_times) * 0.95)], 2
            ) if len(response_times) >= 20 else None,
            "error_count": len(errors),
            "error_rate": round(len(errors) / len(recent), 4),
            "top_endpoints": {
                ep: {
                    "count": len(reqs),
                    "avg_ms": round(
                        sum(r["response_time_ms"] for r in reqs) / len(reqs), 2
                    ),
                }
                for ep, reqs in sorted(
                    by_endpoint.items(), key=lambda x: len(x[1]), reverse=True
                )[:10]
            },
        }

    def get_system_resources(self) -> dict[str, Any]:
        """Get current system resource usage."""
        try:
            load = os.getloadavg()
        except OSError:
            load = (0, 0, 0)

        return {
            "uptime_seconds": time.time() - self._start_time,
            "load_average": {"1m": load[0], "5m": load[1], "15m": load[2]},
            "cpu_count": os.cpu_count() or 1,
        }

    def get_dashboard(self) -> dict[str, Any]:
        """Get complete monitoring dashboard data."""
        return {
            "system": {
                "uptime_seconds": time.time() - self._start_time,
                "resources": self.get_system_resources(),
            },
            "health": self._get_health_summary(),
            "domains": self.get_domain_health(),
            "requests": self.get_request_metrics(),
            "recent_events": self.get_events(limit=20),
            "agents": {
                aid: {
                    "status": a.status,
                    "domain": a.domain,
                    "requests": a.requests_total,
                    "error_rate": round(a.error_rate, 4),
                }
                for aid, a in self.agents.items()
                if a.requests_total > 0
            },
        }
