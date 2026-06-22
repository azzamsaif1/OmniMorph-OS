"""Monitoring API routes — real-time observability and self-healing endpoints.

Provides endpoints for:
- System health dashboard
- Agent health tracking
- Performance analysis
- Self-healing controls
- Event timeline
- Request metrics
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.monitoring.performance_analyzer import PerformanceAnalyzer
from backend.monitoring.system_monitor import SystemMonitor
from backend.monitoring.self_healer import SelfHealer

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Module-level singletons — persist across requests
_analyzer = PerformanceAnalyzer()
_monitor = SystemMonitor()
_healer = SelfHealer(_analyzer)


class MetricRequest(BaseModel):
    name: str
    value: float
    agent: str = "system"
    metadata: dict = {}


class HealingApprovalRequest(BaseModel):
    action_id: str
    approved: bool = True


# ── Dashboard ──


@router.get("/dashboard")
async def monitoring_dashboard():
    """Get the complete monitoring dashboard.

    Returns health status, agent metrics, request stats,
    recent events, and resource usage — all in one call.
    """
    return {
        "system": _monitor.get_dashboard(),
        "performance": {
            "trends": _analyzer.analyze_trends(),
            "health": _analyzer.get_health_report(),
            "recommendations": _analyzer.get_improvement_recommendations()[:10],
        },
        "healing": _healer.get_dashboard(),
    }


# ── Agent Health ──


@router.get("/health")
async def system_health():
    """Get overall system health summary."""
    return _monitor._get_health_summary()


@router.get("/health/agents")
async def all_agents_health():
    """Get health status for all agents."""
    return _monitor.get_agent_health()


@router.get("/health/agents/{agent_id}")
async def agent_health(agent_id: str):
    """Get health status for a specific agent."""
    return _monitor.get_agent_health(agent_id)


@router.get("/health/domains")
async def domain_health():
    """Get health aggregated by domain (security, finance, etc.)."""
    return _monitor.get_domain_health()


# ── Performance Analysis ──


@router.get("/performance/trends")
async def performance_trends():
    """Get performance trends across all metrics."""
    return _analyzer.analyze_trends()


@router.get("/performance/report")
async def performance_report():
    """Get comprehensive health report with detected issues."""
    return _analyzer.get_health_report()


@router.get("/performance/recommendations")
async def improvement_recommendations():
    """Get prioritized improvement recommendations."""
    return _analyzer.get_improvement_recommendations()


@router.post("/metrics")
async def record_metric(req: MetricRequest):
    """Record a performance metric data point."""
    point = _analyzer.record_metric(
        req.name, req.value, req.agent, req.metadata
    )
    # Also record in monitor for agent tracking
    _monitor.record_request(
        agent_id=req.agent,
        endpoint=f"metric:{req.name}",
        response_time_ms=0,
        status_code=200,
    )
    return {
        "recorded": True,
        "metric": req.name,
        "value": req.value,
        "agent": req.agent,
    }


@router.get("/metrics/stats")
async def analyzer_stats():
    """Get performance analyzer statistics."""
    return _analyzer.get_stats()


# ── Event Timeline ──


@router.get("/events")
async def system_events(event_type: str = None, source: str = None, limit: int = 50):
    """Get system events with optional filtering."""
    return _monitor.get_events(event_type, source, limit)


@router.get("/requests")
async def request_metrics(window_seconds: int = 300):
    """Get request metrics for the last N seconds."""
    return _monitor.get_request_metrics(window_seconds)


# ── Self-Healing ──


@router.post("/heal")
async def run_healing_cycle():
    """Run a full diagnostic and healing cycle.

    Analyzes health, detects issues, generates fixes,
    and auto-applies safe optimizations.
    """
    # Record the event
    _monitor.record_event(
        "info", "self_healer", "Healing cycle initiated"
    )
    result = _healer.diagnose_and_heal()
    _monitor.record_event(
        "improvement", "self_healer",
        f"Healing cycle complete: {result['summary']['total_applied']} fixes applied",
        metadata=result["summary"],
    )
    return result


@router.get("/heal/history")
async def healing_history():
    """Get history of all healing actions."""
    return _healer.get_healing_history()


@router.post("/heal/rollback/{action_id}")
async def rollback_action(action_id: str):
    """Rollback a previously applied healing action."""
    result = _healer.rollback_action(action_id)
    if "error" not in result:
        _monitor.record_event(
            "warning", "self_healer",
            f"Rolled back action {action_id}",
            metadata=result,
        )
    return result


@router.get("/heal/params")
async def tunable_parameters():
    """Get all tunable parameters with their current values and ranges."""
    return _healer.get_tunable_params()


# ── System Resources ──


@router.get("/resources")
async def system_resources():
    """Get current system resource usage."""
    return _monitor.get_system_resources()
