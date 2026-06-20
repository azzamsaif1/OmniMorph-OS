"""Tests for auth module — JWT, password hashing, and auth API."""

from __future__ import annotations

import pytest

from backend.auth import create_token, decode_token, hash_password, verify_password


class TestPasswordHashing:
    def test_hash_deterministic(self):
        h1 = hash_password("mypassword")
        h2 = hash_password("mypassword")
        assert h1 == h2

    def test_different_passwords_different_hashes(self):
        h1 = hash_password("password1")
        h2 = hash_password("password2")
        assert h1 != h2

    def test_verify_correct_password(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("secret123")
        assert verify_password("wrong", hashed) is False


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_token("user123", "user@test.com", "developer")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "user@test.com"
        assert payload["role"] == "developer"

    def test_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.token") is None

    def test_tampered_token_returns_none(self):
        token = create_token("user1", "a@b.com")
        parts = token.split(".")
        parts[1] = parts[1] + "x"
        tampered = ".".join(parts)
        assert decode_token(tampered) is None

    def test_token_has_three_parts(self):
        token = create_token("u", "e@e.com")
        assert len(token.split(".")) == 3


@pytest.mark.anyio
async def test_register_user(client):
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "new@test.com",
            "display_name": "New User",
            "password": "pass123",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@test.com"
    assert data["display_name"] == "New User"
    assert "token" in data
    assert "user_id" in data


@pytest.mark.anyio
async def test_register_duplicate_email(client):
    payload = {
        "email": "dup@test.com",
        "display_name": "Dup",
        "password": "p",
    }
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_login_success(client):
    await client.post(
        "/api/auth/register",
        json={"email": "login@test.com", "display_name": "L", "password": "pw"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "login@test.com", "password": "pw"},
    )
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.anyio
async def test_login_wrong_password(client):
    await client.post(
        "/api/auth/register",
        json={"email": "bad@test.com", "display_name": "B", "password": "real"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "bad@test.com", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_me_no_token(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["authenticated"] is False
