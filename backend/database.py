"""Database engine and session management."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import settings
from backend.models import Base
from backend.utils.logger import log

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine  # noqa: PLW0603
    if _engine is None:
        _engine = create_async_engine(settings.postgres_dsn, echo=False, pool_size=10)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory  # noqa: PLW0603
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def init_db() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("database.tables_created")


async def close_db() -> None:
    global _engine, _session_factory  # noqa: PLW0603
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
    log.info("database.closed")
