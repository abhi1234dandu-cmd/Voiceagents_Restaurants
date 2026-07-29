"""Load demo tenant into in-memory store when Supabase is not configured."""

from app.config import get_settings
from app.services.repository import now_iso
from app.services.supabase_client import get_memory_store


def seed_demo_if_needed() -> None:
    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_role_key:
        return
    store = get_memory_store()
    if store.tables.get("organizations"):
        return

    org_id = "11111111-1111-1111-1111-111111111111"
    user_id = "33333333-3333-3333-3333-333333333333"
    rid = "44444444-4444-4444-4444-444444444444"
    menu_id = "66666666-6666-6666-6666-666666666666"
    ts = now_iso()

    store.tables["organizations"] = [
        {
            "id": org_id,
            "name": "Demo Bistro Org",
            "slug": "demo-bistro",
            "stripe_customer_id": None,
            "plan": "pro",
            "status": "active",
            "created_at": ts,
        }
    ]
    store.tables["memberships"] = [
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "org_id": org_id,
            "user_id": user_id,
            "role": "owner",
            "created_at": ts,
        }
    ]
    store.tables["restaurants"] = [
        {
            "id": rid,
            "org_id": org_id,
            "name": "Demo Bistro",
            "timezone": "America/Chicago",
            "phone_e164": "+15555550100",
            "address_json": {"city": "Chicago", "line1": "100 Main St"},
            "transfer_number_e164": "+15555550999",
            "sms_from_number": "+15555550100",
            "hours_json": {"mon-sun": "11:00–22:00"},
            "status": "ready",
            "created_at": ts,
        }
    ]
    store.tables["voice_agents"] = [
        {
            "id": "55555555-5555-5555-5555-555555555555",
            "restaurant_id": rid,
            "twilio_number_sid": "PNdevmock0001",
            "twilio_phone_e164": "+15555550100",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "language": "en",
            "system_prompt": "You are the phone host for Demo Bistro.",
            "greeting": "Thanks for calling Demo Bistro! How can I help you tonight?",
            "transfer_policy_json": {"enabled": True},
            "active": True,
            "created_at": ts,
        }
    ]
    store.tables["menus"] = [
        {"id": menu_id, "restaurant_id": rid, "title": "Main Menu", "version": 1, "published_at": ts}
    ]
    store.tables["menu_items"] = [
        {
            "id": "77777777-7777-7777-7777-777777777771",
            "menu_id": menu_id,
            "name": "Margherita Pizza",
            "description": "Tomato, mozzarella, basil",
            "price_cents": 1400,
            "category": "pizza",
            "allergens_json": ["dairy", "gluten"],
            "available": True,
        },
        {
            "id": "77777777-7777-7777-7777-777777777772",
            "menu_id": menu_id,
            "name": "Caesar Salad",
            "description": "Romaine, parmesan, croutons",
            "price_cents": 900,
            "category": "salads",
            "allergens_json": ["dairy", "gluten"],
            "available": True,
        },
        {
            "id": "77777777-7777-7777-7777-777777777773",
            "menu_id": menu_id,
            "name": "House Red Pasta",
            "description": "Rigatoni, slow tomato, basil oil",
            "price_cents": 1800,
            "category": "pasta",
            "allergens_json": ["gluten"],
            "available": True,
        },
    ]
    store.tables["faqs"] = [
        {
            "id": "88888888-8888-8888-8888-888888888881",
            "restaurant_id": rid,
            "question": "Do you have parking?",
            "answer": "Street parking and a lot behind the restaurant.",
            "tags": ["parking"],
            "active": True,
        },
        {
            "id": "88888888-8888-8888-8888-888888888882",
            "restaurant_id": rid,
            "question": "Are you kid friendly?",
            "answer": "Yes — kids menu and high chairs available.",
            "tags": ["kids"],
            "active": True,
        },
    ]
    store.tables["reservations"] = [
        {
            "id": "99999999-9999-9999-9999-999999999991",
            "restaurant_id": rid,
            "guest_name": "Alex Rivera",
            "guest_phone": "+15555550111",
            "party_size": 4,
            "starts_at": "2026-07-30T19:00:00+00:00",
            "status": "confirmed",
            "source": "voice",
            "notes": None,
            "confirmation_code": "AB12CD",
        }
    ]
    store.tables["calls"] = [
        {
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
            "restaurant_id": rid,
            "twilio_call_sid": "CAdev001",
            "from_number": "+15555550111",
            "to_number": "+15555550100",
            "direction": "inbound",
            "started_at": "2026-07-29T18:02:00+00:00",
            "ended_at": "2026-07-29T18:05:12+00:00",
            "duration_sec": 192,
            "outcome": "reservation_booked",
            "recording_url": None,
            "recording_storage_path": None,
            "cost_estimate_cents": 12,
        }
    ]
    store.tables["call_turns"] = [
        {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1",
            "call_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
            "role": "assistant",
            "content": "Thanks for calling Demo Bistro! How can I help you tonight?",
            "tool_name": None,
            "latency_ms": 40,
            "created_at": ts,
        },
        {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2",
            "call_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
            "role": "user",
            "content": "I'd like a table for four at 7.",
            "tool_name": None,
            "latency_ms": None,
            "created_at": ts,
        },
        {
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3",
            "call_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
            "role": "assistant",
            "content": "Booked for Alex, party of 4. Confirmation AB12CD.",
            "tool_name": "create_reservation",
            "latency_ms": 220,
            "created_at": ts,
        },
    ]
    store.tables["usage_events"] = [
        {
            "id": "cccccccc-cccc-cccc-cccc-ccccccccccc1",
            "org_id": org_id,
            "restaurant_id": rid,
            "call_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
            "metric": "voice_minutes",
            "quantity": 3.2,
            "created_at": ts,
        }
    ]
    store.tables.setdefault("sms_messages", [])
    store.tables.setdefault("billing_subscriptions", [])
    store.tables.setdefault("audit_logs", [])
