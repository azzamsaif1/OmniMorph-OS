"""UCSK — Unified Cognitive Singularity Kernel.

FastAPI entry point: REST + WebSocket endpoints, CORS, lifespan hooks.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.agents import router as agents_router
from backend.api.routes.enterprise import router as enterprise_router
from backend.api.routes.memory import router as memory_router
from backend.api.routes.sensing import router as sensing_router
from backend.api.websocket.guidance import router as guidance_ws_router
from backend.config import settings
from backend.utils.logger import log


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    log.info("ucsk.startup", host=settings.host, port=settings.port)
    yield
    log.info("ucsk.shutdown")


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
app.include_router(sensing_router, prefix="/api/sensing", tags=["sensing"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(enterprise_router, prefix="/api/enterprise", tags=["enterprise"])

# WebSocket routers
app.include_router(guidance_ws_router, prefix="/ws", tags=["websocket"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
