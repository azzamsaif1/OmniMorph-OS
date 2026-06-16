"""Event Store — PostgreSQL + SQLAlchemy for temporal events.

Records every significant event (errors, decisions, state transitions)
with timestamps for the Long-term Engineering Memory (Feature 17).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, JSON, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings
from backend.utils.logger import log


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: uuid4().hex)
    user_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class EventStore:
    """Async PostgreSQL event store."""

    def __init__(self, dsn: str | None = None) -> None:
        self._dsn = dsn or settings.postgres_dsn
        self._engine = create_async_engine(self._dsn, echo=False)
        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False
        )

    async def init_db(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("event_store.tables_created")

    async def record(
        self,
        user_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
        description: str = "",
    ) -> str:
        event = Event(
            user_id=user_id,
            event_type=event_type,
            payload=payload or {},
            description=description,
        )
        async with self._session_factory() as session:
            session.add(event)
            await session.commit()
            log.debug("event_store.recorded", type=event_type, user=user_id)
            return str(event.id)

    async def get_events(
        self,
        user_id: str,
        event_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        stmt = select(Event).where(Event.user_id == user_id)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        stmt = stmt.order_by(Event.created_at.desc()).limit(limit)

        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "event_type": r.event_type,
                    "payload": r.payload,
                    "description": r.description,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]

    async def count_events(self, user_id: str) -> int:
        from sqlalchemy import func

        stmt = select(func.count(Event.id)).where(Event.user_id == user_id)
        async with self._session_factory() as session:
            result = await session.execute(stmt)
            return result.scalar_one()

    async def close(self) -> None:
        await self._engine.dispose()
