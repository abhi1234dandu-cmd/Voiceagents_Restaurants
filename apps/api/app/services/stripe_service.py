from typing import Any, Optional

import stripe

from app.config import Settings


class StripeService:
    def __init__(self, settings: Settings):
        self.settings = settings
        if settings.stripe_secret_key:
            stripe.api_key = settings.stripe_secret_key

    @property
    def enabled(self) -> bool:
        return bool(self.settings.stripe_secret_key)

    def ensure_customer(self, org: dict[str, Any], email: Optional[str] = None) -> str:
        if org.get("stripe_customer_id"):
            return org["stripe_customer_id"]
        if not self.enabled:
            return f"cus_dev_{org['id'][:8]}"
        customer = stripe.Customer.create(
            name=org["name"],
            email=email,
            metadata={"org_id": org["id"]},
        )
        return customer["id"]

    def create_checkout_session(self, customer_id: str, org_id: str) -> str:
        if not self.enabled:
            return f"{self.settings.app_url}/app/billing?session=dev"
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": self.settings.stripe_price_id, "quantity": 1}],
            success_url=f"{self.settings.app_url}/app/billing?success=1",
            cancel_url=f"{self.settings.app_url}/app/billing?canceled=1",
            metadata={"org_id": org_id},
            subscription_data={"metadata": {"org_id": org_id}},
        )
        return session.url

    def create_portal_session(self, customer_id: str) -> str:
        if not self.enabled:
            return f"{self.settings.app_url}/app/billing"
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{self.settings.app_url}/app/billing",
        )
        return session.url

    def construct_event(self, payload: bytes, sig: str) -> Any:
        if not self.settings.stripe_webhook_secret:
            import json

            return json.loads(payload)
        return stripe.Webhook.construct_event(payload, sig, self.settings.stripe_webhook_secret)

    def report_usage(self, subscription_item_id: str, quantity: int) -> None:
        if not self.enabled:
            return
        stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            action="increment",
        )
