"""Auth API — user registration, login, consent management."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from backend.auth import create_token, decode_token, hash_password, verify_password
from backend.utils.logger import log

router = APIRouter()

# In-memory user store for MVP (production uses PostgreSQL via models.py)
_users: dict[str, dict[str, Any]] = {}


class RegisterRequest(BaseModel):
    email: str
    display_name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ConsentUpdate(BaseModel):
    user_id: str
    consent_camera: bool = False
    consent_mic: bool = False
    consent_keyboard: bool = False
    consent_sharing: bool = False


class TokenResponse(BaseModel):
    token: str
    user_id: str
    email: str
    display_name: str


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest) -> dict[str, Any]:
    if req.email in _users:
        raise HTTPException(status_code=400, detail="Email already registered")

    from uuid import uuid4

    user_id = uuid4().hex[:16]
    _users[req.email] = {
        "user_id": user_id,
        "email": req.email,
        "display_name": req.display_name,
        "hashed_password": hash_password(req.password),
        "role": "developer",
        "consent": {},
        "subscription_plan": "free",
    }

    token = create_token(user_id, req.email)
    log.info("auth.registered", email=req.email, user_id=user_id)
    return {
        "token": token,
        "user_id": user_id,
        "email": req.email,
        "display_name": req.display_name,
    }


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest) -> dict[str, Any]:
    user = _users.get(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user["user_id"], req.email, user.get("role", "developer"))
    log.info("auth.login", email=req.email)
    return {
        "token": token,
        "user_id": user["user_id"],
        "email": user["email"],
        "display_name": user["display_name"],
    }


@router.get("/me")
async def get_current_user(token: str = "") -> dict[str, Any]:
    if not token:
        return {"authenticated": False}
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {
        "authenticated": True,
        "user_id": payload["sub"],
        "email": payload["email"],
        "role": payload.get("role", "developer"),
    }


@router.post("/consent")
async def update_consent(req: ConsentUpdate) -> dict[str, Any]:
    for user_data in _users.values():
        if user_data["user_id"] == req.user_id:
            user_data["consent"] = {
                "camera": req.consent_camera,
                "mic": req.consent_mic,
                "keyboard": req.consent_keyboard,
                "sharing": req.consent_sharing,
            }
            log.info("auth.consent_updated", user_id=req.user_id)
            return {"status": "updated", "consent": user_data["consent"]}
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/consent/{user_id}")
async def get_consent(user_id: str) -> dict[str, Any]:
    for user_data in _users.values():
        if user_data["user_id"] == user_id:
            return {
                "user_id": user_id,
                "consent": user_data.get("consent", {}),
            }
    raise HTTPException(status_code=404, detail="User not found")
