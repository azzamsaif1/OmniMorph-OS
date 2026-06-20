"""UCSK — Unified Cognitive Singularity Kernel.

FastAPI entry point: REST + WebSocket endpoints, CORS, lifespan hooks.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.agents import router as agents_router
from backend.api.routes.auth import router as auth_router
from backend.api.routes.billing import router as billing_router
from backend.api.routes.digital_twin import router as twin_router
from backend.api.routes.enterprise import router as enterprise_router
from backend.api.routes.evaluation import router as evaluation_router
from backend.api.routes.governance import router as governance_router
from backend.api.routes.memory import router as memory_router
from backend.api.routes.preferences import router as preferences_router
from backend.api.routes.research import router as research_router
from backend.api.routes.sensing import router as sensing_router
from backend.api.routes.training import router as training_router
from backend.api.websocket.guidance import router as guidance_ws_router
from backend.config import settings
from backend.utils.logger import log


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    log.info("ucsk.startup", host=settings.host, port=settings.port)
    # Initialize database tables
    try:
        from backend.database import init_db
        await init_db()
    except Exception as exc:
        log.warning("ucsk.db_init_skipped", error=str(exc))
    yield
    log.info("ucsk.shutdown")
    try:
        from backend.database import close_db
        await close_db()
    except Exception:
        pass


app = FastAPI(
    title=settings.app_name,
    description=(
        "Unified Cognitive Singularity Kernel — an AI-native adaptive cognitive "
        "operating layer combining multimodal sensing, intelligent agents, and "
        "dynamic interfaces."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(sensing_router, prefix="/api/sensing", tags=["sensing"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(enterprise_router, prefix="/api/enterprise", tags=["enterprise"])
app.include_router(evaluation_router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(training_router, prefix="/api/training", tags=["training"])
app.include_router(twin_router, prefix="/api/twin", tags=["digital-twin"])
app.include_router(governance_router, prefix="/api/governance", tags=["governance"])
app.include_router(research_router, prefix="/api/research", tags=["research"])
app.include_router(billing_router, prefix="/api/billing", tags=["billing"])
app.include_router(preferences_router, prefix="/api/preferences", tags=["preferences"])

# WebSocket routers
app.include_router(guidance_ws_router, prefix="/ws", tags=["websocket"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get("/api/system/info")
async def system_info() -> dict[str, object]:
    """System overview for dashboards and monitoring."""
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "architecture": {
            "layers": [
                "Layer 0: Multimodal Sensing",
                "Layer 1: Cognitive Kernel",
                "Layer 2: Agent Mesh (13 agents)",
                "Layer 3: Collective Memory",
                "Layer 4: Multi-Morph Interface",
                "Layer 5: Cloud Infrastructure",
            ],
            "agents": {
                "supervisors": ["sensory", "analysis", "interface", "execution", "memory"],
                "specialists": [
                    "backend", "lowlevel", "security", "research",
                    "codereview", "testing", "architecture", "devops",
                ],
            },
            "ui_modes": ["visual", "audio", "haptic", "mixed", "zero"],
            "databases": ["qdrant", "neo4j", "postgresql", "redis"],
        },
        "features": [
            "Multimodal Cognitive Sensing",
            "Mental State Classification (85%+ accuracy)",
            "13-Agent Entangled Mesh",
            "Federated Skill Transfer (DP epsilon=1.0)",
            "Digital Twin Export",
            "Competitive Engineering Twin",
            "5-Mode Adaptive UI (<200ms transitions)",
            "Real-world Training Scenarios",
            "Career Evolution Simulator",
            "Enterprise Team Analytics",
            "Privacy-by-Design Governance",
            "Automated Research Intelligence",
        ],
    }
