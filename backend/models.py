"""UCSK Database Models — SQLAlchemy ORM definitions.

Covers users, teams, sessions, agent logs, consent records,
billing subscriptions, and skill-diff sharing history.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(32), default="developer")
    team_id = Column(String(32), ForeignKey("teams.id"), nullable=True)
    consent_camera = Column(Boolean, default=False)
    consent_mic = Column(Boolean, default=False)
    consent_keyboard = Column(Boolean, default=False)
    consent_sharing = Column(Boolean, default=False)
    stripe_customer_id = Column(String(64), nullable=True)
    subscription_plan = Column(String(32), default="free")
    subscription_status = Column(String(32), default="inactive")
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    sessions = relationship("UserSession", back_populates="user")
    team = relationship("Team", back_populates="members")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String(32), primary_key=True, default=_uuid)
    name = Column(String(128), nullable=False)
    org_name = Column(String(128), nullable=True)
    owner_id = Column(String(32), nullable=False)
    plan = Column(String(32), default="team_basic")
    max_members = Column(Integer, default=25)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    members = relationship("User", back_populates="team")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=_utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_sec = Column(Float, default=0.0)
    avg_focus = Column(Float, default=0.0)
    avg_fatigue = Column(Float, default=0.0)
    avg_frustration = Column(Float, default=0.0)
    dominant_state = Column(String(32), default="idle")
    ui_mode_changes = Column(Integer, default=0)
    agent_interactions = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)

    user = relationship("User", back_populates="sessions")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), nullable=False, index=True)
    session_id = Column(String(32), nullable=True, index=True)
    agent_name = Column(String(64), nullable=False, index=True)
    action = Column(String(128), nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    duration_ms = Column(Float, default=0.0)
    model_used = Column(String(64), nullable=True)
    tokens_used = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow, index=True)


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(String(64), nullable=False)
    granted = Column(Boolean, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(256), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class SkillDiffRecord(Base):
    __tablename__ = "skill_diff_records"

    id = Column(String(32), primary_key=True, default=_uuid)
    diff_id = Column(String(32), unique=True, nullable=False, index=True)
    source_anon_id = Column(String(64), nullable=False)
    skill_domain = Column(String(128), nullable=False)
    abstraction = Column(Text, nullable=True)
    difficulty = Column(Float, default=0.5)
    times_applied = Column(Integer, default=0)
    avg_success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(32), primary_key=True, default=_uuid)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    stripe_subscription_id = Column(String(64), nullable=True, unique=True)
    plan = Column(String(32), nullable=False)
    status = Column(String(32), default="active")
    amount_cents = Column(Integer, default=0)
    currency = Column(String(3), default="usd")
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
