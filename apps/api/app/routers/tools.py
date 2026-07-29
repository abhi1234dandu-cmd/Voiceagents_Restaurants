from uuid import UUID

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.deps.auth import require_internal
from app.models.schemas import ToolRequest, ToolResponse
from app.services.repository import Repository
from app.services.twilio_service import TwilioService

router = APIRouter(prefix="/internal/tools", tags=["internal-tools"], dependencies=[Depends(require_internal)])


@router.post("/get_hours", response_model=ToolResponse)
def get_hours(body: ToolRequest):
    repo = Repository()
    restaurant = repo.get_restaurant(body.restaurant_id)
    return ToolResponse(ok=True, result={"hours": restaurant.get("hours_json") or {}, "timezone": restaurant.get("timezone")})


@router.post("/search_faq", response_model=ToolResponse)
def search_faq(body: ToolRequest):
    query = body.args.get("query", "")
    faqs = Repository().search_faqs(body.restaurant_id, query)
    return ToolResponse(ok=True, result={"faqs": faqs})


@router.post("/get_menu_item", response_model=ToolResponse)
def get_menu_item(body: ToolRequest):
    query = body.args.get("query", "")
    items = Repository().search_menu(body.restaurant_id, query)
    return ToolResponse(ok=True, result={"items": items})


@router.post("/check_availability", response_model=ToolResponse)
def check_availability(body: ToolRequest):
    starts_at = body.args.get("starts_at")
    party_size = int(body.args.get("party_size", 2))
    repo = Repository()
    existing = [
        r
        for r in repo.list_reservations(body.restaurant_id)
        if r.get("starts_at") == starts_at and r.get("status") in ("pending", "confirmed")
    ]
    booked = sum(int(r.get("party_size", 0)) for r in existing)
    capacity = 8
    available = booked + party_size <= capacity
    return ToolResponse(ok=True, result={"available": available, "remaining": max(0, capacity - booked)})


@router.post("/create_reservation", response_model=ToolResponse)
def create_reservation(body: ToolRequest):
    repo = Repository()
    try:
        row = repo.create_reservation(
            body.restaurant_id,
            {
                "guest_name": body.args.get("guest_name"),
                "guest_phone": body.args.get("guest_phone"),
                "party_size": int(body.args.get("party_size", 2)),
                "starts_at": body.args.get("starts_at"),
                "notes": body.args.get("notes"),
                "source": "voice",
            },
        )
        if body.call_id:
            repo.update_call(body.call_id, {"outcome": "reservation_booked"})
        return ToolResponse(ok=True, result=row)
    except Exception as exc:
        return ToolResponse(ok=False, error=str(exc))


@router.post("/send_sms_confirmation", response_model=ToolResponse)
def send_sms_confirmation(body: ToolRequest, settings: Settings = Depends(get_settings)):
    repo = Repository()
    restaurant = repo.get_restaurant(body.restaurant_id)
    from_number = restaurant.get("sms_from_number") or restaurant.get("phone_e164")
    to_number = body.args.get("to_number")
    message = body.args.get(
        "body",
        f"Your reservation is confirmed. Code: {body.args.get('confirmation_code', '')}",
    )
    if not from_number or not to_number:
        return ToolResponse(ok=False, error="Missing SMS numbers")
    twilio = TwilioService(settings)
    result = twilio.send_sms(from_number, to_number, message)
    repo.create_sms(
        {
            "restaurant_id": str(body.restaurant_id),
            "call_id": str(body.call_id) if body.call_id else None,
            "to_number": to_number,
            "body": message,
            "status": result.get("status", "queued"),
            "twilio_sid": result.get("sid"),
            "direction": "outbound",
        }
    )
    repo.record_usage(restaurant["org_id"], body.restaurant_id, body.call_id, "sms", 1)
    return ToolResponse(ok=True, result=result)


@router.post("/transfer_to_staff", response_model=ToolResponse)
def transfer_to_staff(body: ToolRequest):
    repo = Repository()
    restaurant = repo.get_restaurant(body.restaurant_id)
    number = restaurant.get("transfer_number_e164")
    if not number:
        return ToolResponse(ok=False, error="No transfer number configured")
    if body.call_id:
        repo.update_call(body.call_id, {"outcome": "transferred"})
    return ToolResponse(ok=True, result={"transfer_number": number, "action": "dial"})


@router.post("/end_call", response_model=ToolResponse)
def end_call(body: ToolRequest):
    if body.call_id:
        Repository().update_call(body.call_id, {"outcome": body.args.get("outcome", "completed")})
    return ToolResponse(ok=True, result={"action": "hangup"})


@router.post("/log_turn", response_model=ToolResponse)
def log_turn(body: ToolRequest):
    if not body.call_id:
        return ToolResponse(ok=False, error="call_id required")
    row = Repository().add_turn(
        {
            "call_id": str(body.call_id),
            "role": body.args.get("role", "assistant"),
            "content": body.args.get("content", ""),
            "tool_name": body.args.get("tool_name"),
            "latency_ms": body.args.get("latency_ms"),
        }
    )
    return ToolResponse(ok=True, result=row)


@router.post("/embed_search", response_model=ToolResponse)
def embed_search(body: ToolRequest):
    """Scale feature: FAQ/menu retrieval with optional embeddings boost."""
    repo = Repository()
    query = body.args.get("query", "")
    faqs = repo.search_faqs(body.restaurant_id, query)
    items = repo.search_menu(body.restaurant_id, query)
    return ToolResponse(ok=True, result={"faqs": faqs, "menu_items": items})
