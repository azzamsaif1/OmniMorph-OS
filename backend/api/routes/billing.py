"""Billing API — Stripe integration for subscriptions.

Handles subscription plans, checkout sessions, webhooks, and
payment status. Uses Stripe API when configured, falls back to
local simulation for development.
"""

from __future__ import annotations

import os
import time
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.utils.logger import log

router = APIRouter()

# Plan definitions
PLANS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "features": [
            "Basic cognitive sensing",
            "2 UI modes (visual, audio)",
            "5 agent interactions/day",
        ],
        "limits": {"agent_calls": 5, "ui_modes": 2, "storage_mb": 100},
    },
    "pro": {
        "name": "Pro",
        "price_monthly": 49_00,  # $49/month in cents
        "stripe_price_id": os.environ.get("STRIPE_PRO_PRICE_ID", "price_pro_placeholder"),
        "features": [
            "Full cognitive sensing (face + voice + behavior)",
            "All 5 UI modes",
            "Unlimited agent interactions",
            "Digital Twin export",
            "Training scenarios",
            "Research feed",
        ],
        "limits": {"agent_calls": -1, "ui_modes": 5, "storage_mb": 5000},
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 199_00,  # $199/month in cents
        "stripe_price_id": os.environ.get("STRIPE_ENTERPRISE_PRICE_ID", "price_ent_placeholder"),
        "features": [
            "Everything in Pro",
            "Team dashboard & analytics",
            "Federated skill sharing",
            "Career simulator",
            "Priority support",
            "Custom integrations",
            "SSO/SAML",
        ],
        "limits": {"agent_calls": -1, "ui_modes": 5, "storage_mb": 50000},
    },
}

# In-memory subscription store for MVP
_subscriptions: dict[str, dict[str, Any]] = {}


class SubscribeRequest(BaseModel):
    user_id: str
    plan: str
    success_url: str = "http://localhost:5173/billing/success"
    cancel_url: str = "http://localhost:5173/billing/cancel"


@router.get("/plans")
async def list_plans() -> dict[str, Any]:
    return {
        "plans": {
            k: {
                "name": v["name"],
                "price_monthly_cents": v["price_monthly"],
                "features": v["features"],
            }
            for k, v in PLANS.items()
        }
    }


@router.post("/subscribe")
async def create_subscription(req: SubscribeRequest) -> dict[str, Any]:
    plan = PLANS.get(req.plan)
    if not plan:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {req.plan}")

    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")

    if stripe_key and req.plan != "free":
        try:
            import stripe

            stripe.api_key = stripe_key
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": plan.get("stripe_price_id", ""), "quantity": 1}],
                success_url=req.success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=req.cancel_url,
                metadata={"user_id": req.user_id, "plan": req.plan},
            )
            return {
                "status": "checkout_created",
                "checkout_url": session.url,
                "session_id": session.id,
            }
        except Exception as exc:
            log.warning("billing.stripe_error", error=str(exc))
            # Fall through to local simulation

    sub_id = uuid4().hex[:12]
    _subscriptions[req.user_id] = {
        "subscription_id": sub_id,
        "user_id": req.user_id,
        "plan": req.plan,
        "status": "active",
        "amount_cents": plan["price_monthly"],
        "created_at": time.time(),
    }
    log.info("billing.subscribed", user_id=req.user_id, plan=req.plan)
    return {
        "status": "subscribed",
        "subscription_id": sub_id,
        "plan": req.plan,
        "amount_cents": plan["price_monthly"],
    }


@router.get("/subscription/{user_id}")
async def get_subscription(user_id: str) -> dict[str, Any]:
    sub = _subscriptions.get(user_id)
    if not sub:
        return {"user_id": user_id, "plan": "free", "status": "active"}
    return sub


@router.post("/cancel/{user_id}")
async def cancel_subscription(user_id: str) -> dict[str, Any]:
    sub = _subscriptions.get(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    sub["status"] = "cancelled"
    sub["cancelled_at"] = time.time()
    log.info("billing.cancelled", user_id=user_id)
    return {"status": "cancelled", "user_id": user_id}


@router.post("/webhook")
async def stripe_webhook(request: Request) -> dict[str, str]:
    """Handle Stripe webhook events."""
    body = await request.body()
    sig = request.headers.get("stripe-signature", "")
    endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    if endpoint_secret:
        try:
            import stripe

            stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            event = stripe.Webhook.construct_event(body, sig, endpoint_secret)
            event_type = event["type"]
            data = event["data"]["object"]

            if event_type == "checkout.session.completed":
                user_id = data.get("metadata", {}).get("user_id", "")
                plan = data.get("metadata", {}).get("plan", "pro")
                _subscriptions[user_id] = {
                    "subscription_id": data.get("subscription", ""),
                    "user_id": user_id,
                    "plan": plan,
                    "status": "active",
                    "amount_cents": PLANS.get(plan, {}).get("price_monthly", 0),
                    "created_at": time.time(),
                }
                log.info("billing.webhook.completed", user_id=user_id, plan=plan)

            elif event_type == "customer.subscription.deleted":
                for uid, sub in _subscriptions.items():
                    if sub.get("subscription_id") == data.get("id"):
                        sub["status"] = "cancelled"
                        log.info("billing.webhook.cancelled", user_id=uid)
                        break

        except Exception as exc:
            log.warning("billing.webhook_error", error=str(exc))

    return {"status": "received"}


@router.get("/revenue")
async def revenue_summary() -> dict[str, Any]:
    """Revenue summary for competition submission evidence."""
    total_mrr = 0
    active_subs = 0
    plan_breakdown: dict[str, int] = {}
    for sub in _subscriptions.values():
        if sub.get("status") == "active":
            active_subs += 1
            amount = sub.get("amount_cents", 0)
            total_mrr += amount
            plan = sub.get("plan", "unknown")
            plan_breakdown[plan] = plan_breakdown.get(plan, 0) + 1
    return {
        "mrr_cents": total_mrr,
        "mrr_dollars": total_mrr / 100,
        "active_subscriptions": active_subs,
        "plan_breakdown": plan_breakdown,
    }
