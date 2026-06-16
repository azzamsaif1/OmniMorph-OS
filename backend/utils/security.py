"""Security utilities — hashing, token helpers, privacy guards."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone


def generate_token(nbytes: int = 32) -> str:
    """Return a URL-safe random token."""
    return secrets.token_urlsafe(nbytes)


def hash_value(value: str, salt: str = "") -> str:
    """SHA-256 hash with optional salt (for anonymised skill-diff IDs)."""
    return hashlib.sha256(f"{salt}{value}".encode()).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """Timing-safe string comparison."""
    return hmac.compare_digest(a.encode(), b.encode())


def expiry_timestamp(hours: int = 24) -> datetime:
    """Return a UTC datetime *hours* from now."""
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def anonymise_user_id(user_id: str) -> str:
    """One-way hash so Skill Diffs never leak real identities."""
    return hash_value(user_id, salt="ucsk-anon-v1")
