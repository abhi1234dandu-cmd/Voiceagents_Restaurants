from uuid import UUID

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.deps.auth import AuthContext, assert_restaurant_org, get_current_user
from app.models.schemas import (
    FAQ,
    FAQCreate,
    MenuItem,
    MenuItemCreate,
    VoiceAgent,
    VoiceAgentUpdate,
)
from app.services.repository import Repository
from app.services.twilio_service import TwilioService

router = APIRouter(prefix="/v1/restaurants/{restaurant_id}", tags=["restaurant-resources"])


def _scoped(restaurant_id: UUID, auth: AuthContext) -> Repository:
    repo = Repository()
    r = repo.get_restaurant(restaurant_id)
    assert_restaurant_org(r, auth.org_id)
    return repo


@router.get("/agent", response_model=VoiceAgent)
def get_agent(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    return _scoped(restaurant_id, auth).get_agent(restaurant_id)


@router.patch("/agent", response_model=VoiceAgent)
def update_agent(
    restaurant_id: UUID, body: VoiceAgentUpdate, auth: AuthContext = Depends(get_current_user)
):
    repo = _scoped(restaurant_id, auth)
    org = repo.get_org(auth.org_id)
    payload = body.model_dump(exclude_unset=True)
    if payload.get("active") is True and org.get("status") not in ("active",):
        from fastapi import HTTPException

        raise HTTPException(402, "Active subscription required to activate agent")
    if payload.get("active") is True and org.get("plan") == "free" and not org.get("stripe_customer_id"):
        # Allow free trial activation in MVP if status active
        pass
    return repo.update_agent(restaurant_id, payload)


@router.post("/twilio/provision-number")
def provision_number(
    restaurant_id: UUID,
    auth: AuthContext = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    repo = _scoped(restaurant_id, auth)
    twilio = TwilioService(settings)
    number = twilio.provision_number()
    agent = repo.update_agent(
        restaurant_id,
        {
            "twilio_number_sid": number["sid"],
            "twilio_phone_e164": number["phone_number"],
        },
    )
    repo.update_restaurant(
        restaurant_id,
        {"phone_e164": number["phone_number"], "sms_from_number": number["phone_number"], "status": "ready"},
    )
    repo.audit(auth.org_id, auth.user_id, "provision_number", "voice_agent", agent["id"], number)
    return {"phone_e164": number["phone_number"], "sid": number["sid"], "mock": number.get("mock", False)}


@router.get("/faqs", response_model=list[FAQ])
def list_faqs(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    return _scoped(restaurant_id, auth).list_faqs(restaurant_id)


@router.post("/faqs", response_model=FAQ)
def create_faq(restaurant_id: UUID, body: FAQCreate, auth: AuthContext = Depends(get_current_user)):
    return _scoped(restaurant_id, auth).create_faq(restaurant_id, body.model_dump())


@router.delete("/faqs/{faq_id}")
def delete_faq(restaurant_id: UUID, faq_id: UUID, auth: AuthContext = Depends(get_current_user)):
    _scoped(restaurant_id, auth).delete_faq(faq_id)
    return {"ok": True}


@router.get("/menu", response_model=list[MenuItem])
def list_menu(restaurant_id: UUID, auth: AuthContext = Depends(get_current_user)):
    return _scoped(restaurant_id, auth).list_menu_items(restaurant_id)


@router.post("/menu", response_model=MenuItem)
def create_menu_item(
    restaurant_id: UUID, body: MenuItemCreate, auth: AuthContext = Depends(get_current_user)
):
    return _scoped(restaurant_id, auth).create_menu_item(restaurant_id, body.model_dump())


@router.delete("/menu/{item_id}")
def delete_menu_item(restaurant_id: UUID, item_id: UUID, auth: AuthContext = Depends(get_current_user)):
    _scoped(restaurant_id, auth).delete_menu_item(item_id)
    return {"ok": True}
