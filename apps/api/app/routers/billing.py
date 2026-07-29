from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.deps.auth import AuthContext, get_current_user
from app.models.schemas import CheckoutSessionResponse
from app.services.repository import Repository
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/v1/billing", tags=["billing"])

PLANS = [
    {"id": "starter", "name": "Starter", "price": "$249/mo", "minutes": 500},
    {"id": "professional", "name": "Professional", "price": "$499/mo", "minutes": 2000},
    {"id": "premium", "name": "Premium", "price": "From $999/mo", "minutes": None},
    {"id": "enterprise", "name": "Enterprise", "price": "From $2,500/mo", "minutes": None},
]


class CheckoutBody(BaseModel):
    plan: str = Field(default="starter", pattern="^(starter|professional|premium)$")


@router.get("/plans")
def list_plans():
    return PLANS


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def checkout(
    body: CheckoutBody | None = None,
    auth: AuthContext = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    plan = (body.plan if body else "starter")
    repo = Repository()
    org = repo.get_org(auth.org_id)
    stripe_svc = StripeService(settings)
    customer_id = stripe_svc.ensure_customer(org, auth.email)
    if customer_id != org.get("stripe_customer_id"):
        repo.update_org(auth.org_id, {"stripe_customer_id": customer_id})
    try:
        url = stripe_svc.create_checkout_session(customer_id, str(auth.org_id), plan=plan)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not settings.stripe_secret_key:
        repo.update_org(auth.org_id, {"plan": plan, "status": "active"})
    return CheckoutSessionResponse(url=url)


@router.post("/portal", response_model=CheckoutSessionResponse)
def portal(auth: AuthContext = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    repo = Repository()
    org = repo.get_org(auth.org_id)
    if not org.get("stripe_customer_id"):
        raise HTTPException(400, "No Stripe customer")
    url = StripeService(settings).create_portal_session(org["stripe_customer_id"])
    return CheckoutSessionResponse(url=url)


@router.get("/usage")
def usage(auth: AuthContext = Depends(get_current_user)):
    return Repository().list_usage(auth.org_id)


@router.get("/entitlements")
def entitlements(auth: AuthContext = Depends(get_current_user)):
    from app.services.plan_limits import limits_for, minutes_remaining

    repo = Repository()
    org = repo.get_org(auth.org_id)
    used = sum(
        float(u.get("quantity", 0))
        for u in repo.list_usage(auth.org_id)
        if u.get("metric") == "voice_minutes"
    )
    limits = limits_for(org.get("plan"))
    return {
        "plan": org.get("plan"),
        "status": org.get("status"),
        "limits": limits,
        "minutes_used": used,
        "minutes_remaining": minutes_remaining(org.get("plan"), used),
        "locations": len(repo.list_restaurants(auth.org_id)),
    }


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    settings: Settings = Depends(get_settings),
):
    payload = await request.body()
    stripe_svc = StripeService(settings)
    try:
        event = stripe_svc.construct_event(payload, stripe_signature or "")
    except Exception as exc:
        raise HTTPException(400, f"Webhook error: {exc}") from exc

    repo = Repository()
    event_type = event["type"] if isinstance(event, dict) else getattr(event, "type", None)
    data = event["data"]["object"] if isinstance(event, dict) else event["data"]["object"]
    if not isinstance(data, dict):
        data = dict(data)

    if event_type in ("checkout.session.completed", "customer.subscription.updated", "customer.subscription.created"):
        org_id = (data.get("metadata") or {}).get("org_id")
        customer = data.get("customer")
        status = data.get("status", "active")
        if event_type == "checkout.session.completed":
            status = "active"
            org_id = org_id or (data.get("metadata") or {}).get("org_id")
            sub_id = data.get("subscription")
        else:
            sub_id = data.get("id")

        if not org_id and customer:
            orgs = [o for o in repo.list_orgs() if o.get("stripe_customer_id") == customer]
            org_id = orgs[0]["id"] if orgs else None

        if org_id:
            plan = "pro" if status in ("active", "trialing") else "free"
            org_status = "active" if status in ("active", "trialing") else "past_due"
            updates = {"plan": plan, "status": org_status}
            if customer:
                updates["stripe_customer_id"] = customer
            repo.update_org(org_id, updates)
            repo.upsert_billing_subscription(
                org_id,
                {
                    "stripe_subscription_id": sub_id,
                    "price_id": settings.stripe_price_id,
                    "status": status,
                    "current_period_end": data.get("current_period_end"),
                    "minutes_included": 500,
                },
            )

    if event_type in ("invoice.payment_failed", "customer.subscription.deleted"):
        org_id = (data.get("metadata") or {}).get("org_id")
        customer = data.get("customer")
        if not org_id and customer:
            orgs = [o for o in repo.list_orgs() if o.get("stripe_customer_id") == customer]
            org_id = orgs[0]["id"] if orgs else None
        if org_id:
            repo.update_org(org_id, {"status": "past_due", "plan": "free"})
            if event_type == "customer.subscription.deleted":
                repo.upsert_billing_subscription(
                    org_id,
                    {
                        "stripe_subscription_id": data.get("id"),
                        "status": "canceled",
                        "price_id": settings.stripe_price_id,
                    },
                )

    return {"received": True}
