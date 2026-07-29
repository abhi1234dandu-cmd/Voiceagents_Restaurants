import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Force in-memory store
os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
os.environ["INTERNAL_API_SECRET"] = "test-secret"
os.environ["APP_URL"] = "http://localhost:3000"

from app.main import app  # noqa: E402
from app.services.supabase_client import get_memory_store, get_supabase  # noqa: E402

USER_ID = "33333333-3333-3333-3333-333333333333"
ORG_ID = "11111111-1111-1111-1111-111111111111"
REST_ID = "44444444-4444-4444-4444-444444444444"
DEV_TOKEN = f"dev:{USER_ID}:{ORG_ID}:owner"
AUTH = {"Authorization": f"Bearer {DEV_TOKEN}"}
INTERNAL = {"X-Internal-Secret": "test-secret"}


@pytest.fixture(autouse=True)
def reset_store():
    get_supabase.cache_clear()
    get_memory_store.cache_clear()
    store = get_memory_store()
    store.tables.clear()
    store.tables["organizations"] = [
        {
            "id": ORG_ID,
            "name": "Demo Bistro Org",
            "slug": "demo-bistro",
            "stripe_customer_id": None,
            "plan": "pro",
            "status": "active",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    store.tables["memberships"] = [
        {
            "id": str(uuid4()),
            "org_id": ORG_ID,
            "user_id": USER_ID,
            "role": "owner",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    store.tables["restaurants"] = [
        {
            "id": REST_ID,
            "org_id": ORG_ID,
            "name": "Demo Bistro",
            "timezone": "America/Chicago",
            "phone_e164": "+15555550100",
            "address_json": {},
            "transfer_number_e164": "+15555550999",
            "sms_from_number": "+15555550100",
            "hours_json": {"mon-sun": "11:00-22:00"},
            "status": "ready",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    store.tables["voice_agents"] = [
        {
            "id": str(uuid4()),
            "restaurant_id": REST_ID,
            "twilio_number_sid": None,
            "twilio_phone_e164": "+15555550100",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "language": "en",
            "system_prompt": "You are a helpful restaurant phone assistant.",
            "greeting": "Thanks for calling Demo Bistro!",
            "transfer_policy_json": {"enabled": True},
            "active": True,
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    store.tables["menus"] = [
        {
            "id": "66666666-6666-6666-6666-666666666666",
            "restaurant_id": REST_ID,
            "title": "Main Menu",
            "version": 1,
            "published_at": "2026-01-01T00:00:00Z",
        }
    ]
    store.tables["menu_items"] = [
        {
            "id": str(uuid4()),
            "menu_id": "66666666-6666-6666-6666-666666666666",
            "name": "Margherita Pizza",
            "description": "Tomato, mozzarella, basil",
            "price_cents": 1400,
            "category": "pizza",
            "allergens_json": [],
            "available": True,
        }
    ]
    store.tables["faqs"] = [
        {
            "id": str(uuid4()),
            "restaurant_id": REST_ID,
            "question": "Do you have parking?",
            "answer": "Street parking and a lot behind the restaurant.",
            "tags": ["parking"],
            "active": True,
        }
    ]
    store.tables.setdefault("reservations", [])
    store.tables.setdefault("calls", [])
    store.tables.setdefault("call_turns", [])
    store.tables.setdefault("sms_messages", [])
    store.tables.setdefault("billing_subscriptions", [])
    store.tables.setdefault("usage_events", [])
    store.tables.setdefault("audit_logs", [])
    yield


@pytest.fixture
def client():
    return TestClient(app)
