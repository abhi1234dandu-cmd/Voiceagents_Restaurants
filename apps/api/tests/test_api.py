USER_ID = "33333333-3333-3333-3333-333333333333"
ORG_ID = "11111111-1111-1111-1111-111111111111"
REST_ID = "44444444-4444-4444-4444-444444444444"
DEV_TOKEN = f"dev:{USER_ID}:{ORG_ID}:owner"
AUTH = {"Authorization": f"Bearer {DEV_TOKEN}"}
INTERNAL = {"X-Internal-Secret": "test-secret"}


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_auth_required(client):
    assert client.get("/v1/restaurants").status_code == 401


def test_list_restaurants(client):
    res = client.get("/v1/restaurants", headers=AUTH)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "Demo Bistro"


def test_create_restaurant_blocked_at_plan_cap(client):
    """pro/starter allow 1 location; seed already has Demo Bistro."""
    res = client.post(
        "/v1/restaurants",
        headers=AUTH,
        json={"name": "Second Spot", "timezone": "America/New_York"},
    )
    assert res.status_code == 402


def test_create_restaurant_on_premium(client):
    from app.services.supabase_client import get_memory_store

    get_memory_store().tables["organizations"][0]["plan"] = "premium"
    res = client.post(
        "/v1/restaurants",
        headers=AUTH,
        json={"name": "Second Spot", "timezone": "America/New_York"},
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Second Spot"
    agent = client.get(f"/v1/restaurants/{res.json()['id']}/agent", headers=AUTH)
    assert agent.status_code == 200
    assert agent.json()["voice_id"]


def test_update_agent_voice_id(client):
    res = client.patch(
        f"/v1/restaurants/{REST_ID}/agent",
        headers=AUTH,
        json={"voice_id": "customVoice123", "greeting": "Hello from Demo!"},
    )
    assert res.status_code == 200
    assert res.json()["voice_id"] == "customVoice123"
    assert res.json()["greeting"] == "Hello from Demo!"


def test_faqs_and_menu(client):
    faqs = client.get(f"/v1/restaurants/{REST_ID}/faqs", headers=AUTH)
    assert faqs.status_code == 200
    assert len(faqs.json()) >= 1
    menu = client.get(f"/v1/restaurants/{REST_ID}/menu", headers=AUTH)
    assert menu.status_code == 200
    assert any(i["name"] == "Margherita Pizza" for i in menu.json())


def test_reservation_flow(client):
    res = client.post(
        f"/v1/restaurants/{REST_ID}/reservations",
        headers=AUTH,
        json={
            "guest_name": "Ada",
            "guest_phone": "+15555550001",
            "party_size": 2,
            "starts_at": "2026-08-01T19:00:00Z",
        },
    )
    assert res.status_code == 200
    code = res.json()["confirmation_code"]
    assert code
    cancel = client.post(f"/v1/reservations/{res.json()['id']}/cancel", headers=AUTH)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"


def test_tools_hours_and_faq(client):
    hours = client.post(
        "/internal/tools/get_hours",
        headers=INTERNAL,
        json={"restaurant_id": REST_ID, "args": {}},
    )
    assert hours.status_code == 200
    assert hours.json()["ok"] is True
    faq = client.post(
        "/internal/tools/search_faq",
        headers=INTERNAL,
        json={"restaurant_id": REST_ID, "args": {"query": "parking"}},
    )
    assert faq.status_code == 200
    assert faq.json()["result"]["faqs"]


def test_tools_create_reservation(client):
    res = client.post(
        "/internal/tools/create_reservation",
        headers=INTERNAL,
        json={
            "restaurant_id": REST_ID,
            "args": {
                "guest_name": "Bob",
                "guest_phone": "+15555550002",
                "party_size": 3,
                "starts_at": "2026-08-02T18:00:00Z",
            },
        },
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
    assert res.json()["result"]["confirmation_code"]


def test_stripe_webhook_upsert(client):
    payload = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_test_123",
                "customer": "cus_test",
                "status": "active",
                "metadata": {"org_id": ORG_ID},
                "current_period_end": 1893456000,
            }
        },
    }
    res = client.post("/v1/billing/webhooks/stripe", json=payload)
    assert res.status_code == 200
    org = client.get("/v1/orgs/me", headers=AUTH)
    assert org.json()["plan"] == "pro"
    sub = client.get("/v1/orgs/me/subscription", headers=AUTH)
    assert sub.json()["stripe_subscription_id"] == "sub_test_123"


def test_analytics_summary(client):
    res = client.get("/v1/analytics/summary", headers=AUTH)
    assert res.status_code == 200
    assert "total_calls" in res.json()


def test_org_me(client):
    res = client.get("/v1/orgs/me", headers=AUTH)
    assert res.status_code == 200
    assert res.json()["id"] == ORG_ID
