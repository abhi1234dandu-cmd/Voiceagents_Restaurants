from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException

from app.services.supabase_client import get_supabase


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid4())


def confirmation_code(n: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def slugify(name: str) -> str:
    base = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    return f"{base}-{secrets.token_hex(2)}"


class Repository:
    def __init__(self) -> None:
        self.sb = get_supabase()

    def create_org_for_user(self, user_id: UUID, name: str) -> dict[str, Any]:
        org_id = new_id()
        org = {
            "id": org_id,
            "name": name,
            "slug": slugify(name),
            "stripe_customer_id": None,
            "plan": "free",
            "status": "active",
            "created_at": now_iso(),
        }
        self.sb.table("organizations").insert(org).execute()
        membership = {
            "id": new_id(),
            "org_id": org_id,
            "user_id": str(user_id),
            "role": "owner",
            "created_at": now_iso(),
        }
        self.sb.table("memberships").insert(membership).execute()
        return org

    def get_org(self, org_id: UUID) -> dict[str, Any]:
        res = self.sb.table("organizations").select("*").eq("id", str(org_id)).limit(1).execute()
        if not res.data:
            raise HTTPException(404, "Organization not found")
        return res.data[0]

    def list_restaurants(self, org_id: UUID) -> list[dict[str, Any]]:
        res = self.sb.table("restaurants").select("*").eq("org_id", str(org_id)).execute()
        return res.data or []

    def get_restaurant(self, restaurant_id: UUID) -> dict[str, Any]:
        res = self.sb.table("restaurants").select("*").eq("id", str(restaurant_id)).limit(1).execute()
        if not res.data:
            raise HTTPException(404, "Restaurant not found")
        return res.data[0]

    def create_restaurant(self, org_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        rid = new_id()
        row = {
            "id": rid,
            "org_id": str(org_id),
            "status": "draft",
            "phone_e164": None,
            "sms_from_number": None,
            "created_at": now_iso(),
            **payload,
        }
        self.sb.table("restaurants").insert(row).execute()
        agent = {
            "id": new_id(),
            "restaurant_id": rid,
            "twilio_number_sid": None,
            "twilio_phone_e164": None,
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "language": "en",
            "system_prompt": "You are a helpful restaurant phone assistant.",
            "greeting": f"Thanks for calling {payload.get('name', 'us')}. How can I help you today?",
            "transfer_policy_json": {"enabled": True},
            "active": False,
            "created_at": now_iso(),
        }
        self.sb.table("voice_agents").insert(agent).execute()
        menu = {
            "id": new_id(),
            "restaurant_id": rid,
            "title": "Main Menu",
            "version": 1,
            "published_at": now_iso(),
        }
        self.sb.table("menus").insert(menu).execute()
        return row

    def update_restaurant(self, restaurant_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        cleaned = {k: v for k, v in payload.items() if v is not None}
        res = self.sb.table("restaurants").update(cleaned).eq("id", str(restaurant_id)).execute()
        if not res.data:
            raise HTTPException(404, "Restaurant not found")
        return res.data[0]

    def get_agent(self, restaurant_id: UUID) -> dict[str, Any]:
        res = (
            self.sb.table("voice_agents")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .limit(1)
            .execute()
        )
        if not res.data:
            raise HTTPException(404, "Voice agent not found")
        return res.data[0]

    def update_agent(self, restaurant_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        cleaned = {k: v for k, v in payload.items() if v is not None}
        res = (
            self.sb.table("voice_agents")
            .update(cleaned)
            .eq("restaurant_id", str(restaurant_id))
            .execute()
        )
        if not res.data:
            raise HTTPException(404, "Voice agent not found")
        return res.data[0]

    def get_agent_by_phone(self, phone_e164: str) -> Optional[dict[str, Any]]:
        res = (
            self.sb.table("voice_agents")
            .select("*")
            .eq("twilio_phone_e164", phone_e164)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def list_faqs(self, restaurant_id: UUID) -> list[dict[str, Any]]:
        return (
            self.sb.table("faqs")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .execute()
            .data
            or []
        )

    def create_faq(self, restaurant_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        row = {"id": new_id(), "restaurant_id": str(restaurant_id), **payload}
        self.sb.table("faqs").insert(row).execute()
        return row

    def delete_faq(self, faq_id: UUID) -> None:
        self.sb.table("faqs").delete().eq("id", str(faq_id)).execute()

    def get_menu(self, restaurant_id: UUID) -> Optional[dict[str, Any]]:
        res = (
            self.sb.table("menus")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def list_menu_items(self, restaurant_id: UUID) -> list[dict[str, Any]]:
        menu = self.get_menu(restaurant_id)
        if not menu:
            return []
        return (
            self.sb.table("menu_items").select("*").eq("menu_id", menu["id"]).execute().data or []
        )

    def create_menu_item(self, restaurant_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        menu = self.get_menu(restaurant_id)
        if not menu:
            raise HTTPException(404, "Menu not found")
        row = {"id": new_id(), "menu_id": menu["id"], **payload}
        self.sb.table("menu_items").insert(row).execute()
        return row

    def delete_menu_item(self, item_id: UUID) -> None:
        self.sb.table("menu_items").delete().eq("id", str(item_id)).execute()

    def list_reservations(self, restaurant_id: UUID) -> list[dict[str, Any]]:
        return (
            self.sb.table("reservations")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .order("starts_at", desc=False)
            .execute()
            .data
            or []
        )

    def create_reservation(self, restaurant_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        # Simple conflict: same starts_at already confirmed
        existing = (
            self.sb.table("reservations")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .eq("starts_at", payload["starts_at"] if isinstance(payload["starts_at"], str) else payload["starts_at"].isoformat())
            .execute()
            .data
            or []
        )
        active = [r for r in existing if r.get("status") in ("pending", "confirmed")]
        capacity = 8
        booked = sum(int(r.get("party_size", 0)) for r in active)
        if booked + int(payload["party_size"]) > capacity:
            raise HTTPException(409, "No availability for that time")
        starts = payload["starts_at"]
        if hasattr(starts, "isoformat"):
            starts = starts.isoformat()
        row = {
            "id": new_id(),
            "restaurant_id": str(restaurant_id),
            "status": "confirmed",
            "confirmation_code": confirmation_code(),
            **{**payload, "starts_at": starts},
        }
        self.sb.table("reservations").insert(row).execute()
        return row

    def cancel_reservation(self, reservation_id: UUID) -> dict[str, Any]:
        res = (
            self.sb.table("reservations")
            .update({"status": "cancelled"})
            .eq("id", str(reservation_id))
            .execute()
        )
        if not res.data:
            raise HTTPException(404, "Reservation not found")
        return res.data[0]

    def create_call(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = {"id": new_id(), "started_at": now_iso(), **payload}
        self.sb.table("calls").insert(row).execute()
        return row

    def update_call(self, call_id: str | UUID, payload: dict[str, Any]) -> dict[str, Any]:
        res = self.sb.table("calls").update(payload).eq("id", str(call_id)).execute()
        return res.data[0] if res.data else {}

    def get_call_by_sid(self, sid: str) -> Optional[dict[str, Any]]:
        res = self.sb.table("calls").select("*").eq("twilio_call_sid", sid).limit(1).execute()
        return res.data[0] if res.data else None

    def list_calls(self, restaurant_id: UUID) -> list[dict[str, Any]]:
        return (
            self.sb.table("calls")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .order("started_at", desc=True)
            .execute()
            .data
            or []
        )

    def get_call(self, call_id: UUID) -> dict[str, Any]:
        res = self.sb.table("calls").select("*").eq("id", str(call_id)).limit(1).execute()
        if not res.data:
            raise HTTPException(404, "Call not found")
        return res.data[0]

    def add_turn(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = {"id": new_id(), "created_at": now_iso(), **payload}
        self.sb.table("call_turns").insert(row).execute()
        return row

    def list_turns(self, call_id: UUID) -> list[dict[str, Any]]:
        return (
            self.sb.table("call_turns")
            .select("*")
            .eq("call_id", str(call_id))
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )

    def create_sms(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = {"id": new_id(), **payload}
        self.sb.table("sms_messages").insert(row).execute()
        return row

    def list_sms_for_phone(self, restaurant_id: UUID, phone: str) -> list[dict[str, Any]]:
        return (
            self.sb.table("sms_messages")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .eq("to_number", phone)
            .execute()
            .data
            or []
        )

    def record_usage(
        self, org_id: UUID, restaurant_id: Optional[UUID], call_id: Optional[UUID], metric: str, quantity: float
    ) -> dict[str, Any]:
        row = {
            "id": new_id(),
            "org_id": str(org_id),
            "restaurant_id": str(restaurant_id) if restaurant_id else None,
            "call_id": str(call_id) if call_id else None,
            "metric": metric,
            "quantity": quantity,
            "created_at": now_iso(),
        }
        self.sb.table("usage_events").insert(row).execute()
        return row

    def list_usage(self, org_id: UUID) -> list[dict[str, Any]]:
        return self.sb.table("usage_events").select("*").eq("org_id", str(org_id)).execute().data or []

    def list_orgs(self) -> list[dict[str, Any]]:
        return self.sb.table("organizations").select("*").execute().data or []

    def update_org(self, org_id: UUID, payload: dict[str, Any]) -> dict[str, Any]:
        res = self.sb.table("organizations").update(payload).eq("id", str(org_id)).execute()
        return res.data[0] if res.data else {}

    def upsert_billing_subscription(self, org_id: str | UUID, payload: dict[str, Any]) -> dict[str, Any]:
        existing = (
            self.sb.table("billing_subscriptions")
            .select("*")
            .eq("org_id", str(org_id))
            .limit(1)
            .execute()
            .data
            or []
        )
        row = {
            "org_id": str(org_id),
            "minutes_included": 500,
            "minutes_used": 0,
            **payload,
        }
        if existing:
            res = (
                self.sb.table("billing_subscriptions")
                .update(row)
                .eq("id", existing[0]["id"])
                .execute()
            )
            return res.data[0] if res.data else {**existing[0], **row}
        row = {"id": new_id(), **row}
        self.sb.table("billing_subscriptions").insert(row).execute()
        return row

    def list_memberships(self, org_id: UUID) -> list[dict[str, Any]]:
        return (
            self.sb.table("memberships").select("*").eq("org_id", str(org_id)).execute().data or []
        )

    def get_billing_subscription(self, org_id: UUID) -> Optional[dict[str, Any]]:
        res = (
            self.sb.table("billing_subscriptions")
            .select("*")
            .eq("org_id", str(org_id))
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    def audit(self, org_id: UUID, actor: Optional[UUID], action: str, entity: str, entity_id: str, meta: dict[str, Any] | None = None) -> None:
        self.sb.table("audit_logs").insert(
            {
                "id": new_id(),
                "org_id": str(org_id),
                "actor_user_id": str(actor) if actor else None,
                "action": action,
                "entity": entity,
                "entity_id": entity_id,
                "meta_json": meta or {},
                "created_at": now_iso(),
            }
        ).execute()

    def search_faqs(self, restaurant_id: UUID, query: str) -> list[dict[str, Any]]:
        faqs = self.list_faqs(restaurant_id)
        q = query.lower()
        scored = []
        for f in faqs:
            if not f.get("active", True):
                continue
            text = f"{f.get('question', '')} {f.get('answer', '')}".lower()
            score = sum(1 for token in q.split() if token in text)
            # embedding similarity stub: if embedding present, boost when query tokens overlap
            if f.get("embedding"):
                score += 0.5
            if score:
                scored.append((score, f))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in scored[:5]]

    def search_menu(self, restaurant_id: UUID, query: str) -> list[dict[str, Any]]:
        items = self.list_menu_items(restaurant_id)
        q = query.lower()
        return [
            i
            for i in items
            if i.get("available", True)
            and (q in i.get("name", "").lower() or q in i.get("description", "").lower() or q in i.get("category", "").lower())
        ][:10]
