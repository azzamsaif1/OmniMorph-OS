"""Tests for billing API — plans, subscriptions, revenue."""

from __future__ import annotations

import pytest


@pytest.mark.anyio
async def test_list_plans_returns_three_plans(client):
    resp = await client.get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()["plans"]
    assert "free" in plans
    assert "pro" in plans
    assert "enterprise" in plans


@pytest.mark.anyio
async def test_plan_prices_correct(client):
    resp = await client.get("/api/billing/plans")
    plans = resp.json()["plans"]
    assert plans["free"]["price_monthly_cents"] == 0
    assert plans["pro"]["price_monthly_cents"] == 4900
    assert plans["enterprise"]["price_monthly_cents"] == 19900


@pytest.mark.anyio
async def test_plan_features(client):
    resp = await client.get("/api/billing/plans")
    plans = resp.json()["plans"]
    assert "Basic cognitive sensing" in plans["free"]["features"]
    assert "Digital Twin export" in plans["pro"]["features"]
    assert "SSO/SAML" in plans["enterprise"]["features"]


@pytest.mark.anyio
async def test_subscribe_free_plan(client):
    resp = await client.post(
        "/api/billing/subscribe",
        json={"user_id": "test-user", "plan": "free"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "subscribed"
    assert data["plan"] == "free"
    assert data["amount_cents"] == 0


@pytest.mark.anyio
async def test_subscribe_unknown_plan_returns_400(client):
    resp = await client.post(
        "/api/billing/subscribe",
        json={"user_id": "test-user", "plan": "nonexistent"},
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_subscription_default_is_free(client):
    resp = await client.get("/api/billing/subscription/unsubscribed-user")
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "free"
    assert data["status"] == "active"


@pytest.mark.anyio
async def test_revenue_summary(client):
    resp = await client.get("/api/billing/revenue")
    assert resp.status_code == 200
    data = resp.json()
    assert "mrr_cents" in data
    assert "mrr_dollars" in data
    assert "active_subscriptions" in data
    assert "plan_breakdown" in data
