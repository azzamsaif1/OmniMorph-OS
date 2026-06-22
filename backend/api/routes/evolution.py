"""Evolution API routes — self-evolving penetration testing endpoints.

Exposes the EvolutionEngine for autonomous security assessments
with learning, strategy evolution, and self-improvement.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.security.evolution.evolution_engine import EvolutionEngine

router = APIRouter(prefix="/api/evolution", tags=["evolution"])

# Module-level singleton — state persists across requests
_engine = EvolutionEngine()


class AssessmentRequest(BaseModel):
    target_ip: str
    depth: str = "standard"  # quick|standard|deep


class PredictionRequest(BaseModel):
    target_type: str  # network|host|service|application
    technique: str  # scan|exploit|bruteforce
    defenses: list[str] = []


class ExperienceRequest(BaseModel):
    target_type: str
    technique: str
    outcome: str  # success|failure|partial|blocked
    target_info: dict = {}
    defenses_encountered: list[str] = []
    tactics_used: list[str] = []
    lessons_learned: list[str] = []
    confidence: float = 0.5


@router.post("/assess")
async def autonomous_assessment(req: AssessmentRequest):
    """Run a full autonomous penetration test with self-evolution.

    The engine:
    1. Scans the target (C-based recon agent)
    2. Correlates vulnerabilities (C-based vuln analyzer)
    3. Simulates exploits (C-based exploit agent)
    4. Records all outcomes in experience memory
    5. Evolves strategies based on results
    6. Self-assesses and generates improvements
    """
    return await _engine.run_autonomous_assessment(req.target_ip, req.depth)


@router.post("/predict")
async def predict_attack_success(req: PredictionRequest):
    """Predict success probability for an attack approach.

    Uses accumulated experience and strategy data to estimate
    likelihood of success before attempting.
    """
    return _engine.learner.predict_success(
        req.target_type, req.technique, req.defenses
    )


@router.post("/experience")
async def record_experience(req: ExperienceRequest):
    """Manually record an attack experience for learning."""
    exp = _engine.memory.record_experience(
        target_type=req.target_type,
        technique=req.technique,
        outcome=req.outcome,
        target_info=req.target_info,
        defenses_encountered=req.defenses_encountered,
        tactics_used=req.tactics_used,
        lessons_learned=req.lessons_learned,
        confidence=req.confidence,
    )
    learning = _engine.learner.learn_from_experience(exp)
    return {
        "experience_id": exp.id,
        "learning_updates": learning,
    }


@router.post("/evolve")
async def evolve_strategies():
    """Trigger one strategy evolution cycle.

    Mutates underperforming strategies, borrows from top performers,
    and retires consistently failing approaches.
    """
    return _engine.learner.evolve_strategies()


@router.get("/dashboard")
async def evolution_dashboard():
    """Get the complete evolution dashboard.

    Includes: performance metrics, strategy stats, memory stats,
    improvement log, and comparison vs single-model approaches.
    """
    return _engine.get_evolution_dashboard()


@router.get("/strategies")
async def list_strategies():
    """List all attack strategies with their success rates."""
    return {
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "target_type": s.target_type,
                "phases": s.phases,
                "success_rate": s.success_rate,
                "times_used": s.times_used,
                "generation": s.generation,
                "defense_bypasses": s.defense_bypasses,
            }
            for s in _engine.learner.strategies.values()
        ],
        "total": len(_engine.learner.strategies),
        "avg_success_rate": _engine.learner.get_stats()["avg_success_rate"],
    }


@router.get("/memory")
async def experience_memory():
    """Get experience memory statistics and recent experiences."""
    stats = _engine.memory.get_stats()
    recent = _engine.memory.experiences[-20:]

    return {
        "stats": stats,
        "recent_experiences": [
            {
                "id": e.id,
                "target_type": e.target_type,
                "technique": e.technique,
                "outcome": e.outcome,
                "confidence": e.confidence,
                "lessons_learned": e.lessons_learned,
                "timestamp": e.timestamp,
            }
            for e in recent
        ],
        "success_strategies": _engine.memory.success_strategies,
        "failure_patterns": _engine.memory.failure_patterns,
    }


@router.get("/metrics")
async def performance_metrics():
    """Get current performance metrics and targets."""
    return {
        "current_metrics": dict(_engine.metrics),
        "targets": {
            "detection_rate": 0.95,
            "vuln_precision": 0.90,
            "exploit_success": 0.85,
            "false_positive_rate": 0.05,
        },
        "assessments_completed": _engine.assessments_completed,
        "total_vulns_found": _engine.total_vulns_found,
        "total_exploits_succeeded": _engine.total_exploits_succeeded,
        "improvement_log": _engine.improvement_log[-10:],
    }
