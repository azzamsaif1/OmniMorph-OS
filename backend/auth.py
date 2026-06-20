"""Authentication — JWT-based user auth with password hashing."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Any

from backend.config import settings
from backend.utils.logger import log

_SECRET = "ucsk-jwt-secret-2026"
_ALGORITHM = "HS256"
_EXPIRY_SEC = 86400  # 24 hours


def hash_password(password: str) -> str:
    salt = "ucsk-pw-salt-2026"
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed)


def create_token(user_id: str, email: str, role: str = "developer") -> str:
    header = urlsafe_b64encode(json.dumps({"alg": _ALGORITHM, "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = urlsafe_b64encode(
        json.dumps(
            {
                "sub": user_id,
                "email": email,
                "role": role,
                "iat": int(time.time()),
                "exp": int(time.time()) + _EXPIRY_SEC,
            }
        ).encode()
    ).decode().rstrip("=")
    sig = _sign(f"{header}.{payload}")
    return f"{header}.{payload}.{sig}"


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig = parts
        if not hmac.compare_digest(_sign(f"{header_b64}.{payload_b64}"), sig):
            return None
        padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(urlsafe_b64decode(padded))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def _sign(data: str) -> str:
    return urlsafe_b64encode(
        hmac.new(_SECRET.encode(), data.encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
