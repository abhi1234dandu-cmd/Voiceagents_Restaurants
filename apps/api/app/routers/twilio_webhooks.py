from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import PlainTextResponse

from app.config import Settings, get_settings
from app.services.repository import Repository
from app.services.twilio_service import TwilioService

router = APIRouter(prefix="/webhooks/twilio", tags=["twilio-webhooks"])


@router.post("/voice")
async def inbound_voice(request: Request, settings: Settings = Depends(get_settings)):
    form = dict(await request.form())
    signature = request.headers.get("X-Twilio-Signature", "")
    twilio = TwilioService(settings)
    url = str(request.url)
    if not twilio.validate_signature(url, form, signature):
        return Response(status_code=403, content="Invalid signature")

    to_number = form.get("To", "")
    from_number = form.get("From", "")
    call_sid = form.get("CallSid", "")
    repo = Repository()
    agent = repo.get_agent_by_phone(to_number)
    restaurant_id = agent["restaurant_id"] if agent else None
    if not restaurant_id:
        # Try match restaurants.phone_e164
        # Fallback: reject
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Say>Sorry, this number is not configured.</Say><Hangup/></Response>"""
        return PlainTextResponse(twiml, media_type="application/xml")

    call = repo.create_call(
        {
            "restaurant_id": restaurant_id,
            "twilio_call_sid": call_sid,
            "from_number": from_number,
            "to_number": to_number,
            "direction": "inbound",
            "outcome": "in_progress",
        }
    )

    voice_id = (agent or {}).get("voice_id") or settings.elevenlabs_default_voice_id
    greeting = (agent or {}).get("greeting") or "Thanks for calling. How can I help you today?"
    # Escape XML-sensitive chars in attribute values
    def _xml(s: str) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    ws_url = settings.voice_worker_ws_url
    # Twilio Media Streams require wss in production.
    # Speech path: OpenAI LLM+tools → ElevenLabs TTS (voice_id per restaurant).
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{ws_url}">
      <Parameter name="call_id" value="{_xml(call['id'])}" />
      <Parameter name="restaurant_id" value="{_xml(restaurant_id)}" />
      <Parameter name="from_number" value="{_xml(from_number)}" />
      <Parameter name="voice_id" value="{_xml(voice_id)}" />
      <Parameter name="greeting" value="{_xml(greeting)}" />
    </Stream>
  </Connect>
</Response>"""
    return PlainTextResponse(twiml, media_type="application/xml")


@router.post("/status")
async def call_status(request: Request, settings: Settings = Depends(get_settings)):
    form = dict(await request.form())
    twilio = TwilioService(settings)
    if not twilio.validate_signature(str(request.url), form, request.headers.get("X-Twilio-Signature", "")):
        return Response(status_code=403)
    repo = Repository()
    call = repo.get_call_by_sid(form.get("CallSid", ""))
    if call:
        duration = int(form.get("CallDuration") or 0)
        repo.update_call(
            call["id"],
            {
                "ended_at": form.get("Timestamp"),
                "duration_sec": duration,
                "outcome": form.get("CallStatus", call.get("outcome")),
            },
        )
        restaurant = repo.get_restaurant(call["restaurant_id"])
        minutes = round(duration / 60.0, 2)
        repo.record_usage(restaurant["org_id"], restaurant["id"], call["id"], "voice_minutes", minutes)
    return {"ok": True}


@router.post("/recording")
async def recording_ready(request: Request, settings: Settings = Depends(get_settings)):
    form = dict(await request.form())
    twilio = TwilioService(settings)
    if not twilio.validate_signature(str(request.url), form, request.headers.get("X-Twilio-Signature", "")):
        return Response(status_code=403)
    repo = Repository()
    call = repo.get_call_by_sid(form.get("CallSid", ""))
    if call:
        recording_url = form.get("RecordingUrl", "")
        path = f"recordings/{call['restaurant_id']}/{call['id']}.wav"
        repo.update_call(
            call["id"],
            {"recording_url": recording_url, "recording_storage_path": path},
        )
    return {"ok": True}


@router.post("/sms")
async def inbound_sms(request: Request, settings: Settings = Depends(get_settings)):
    """Two-way SMS: guests can reply CHANGE or CANCEL + confirmation code."""
    form = dict(await request.form())
    twilio = TwilioService(settings)
    if not twilio.validate_signature(str(request.url), form, request.headers.get("X-Twilio-Signature", "")):
        return Response(status_code=403)

    body = (form.get("Body") or "").strip()
    from_number = form.get("From", "")
    to_number = form.get("To", "")
    repo = Repository()
    agent = repo.get_agent_by_phone(to_number)
    if not agent:
        return PlainTextResponse(
            '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml",
        )

    restaurant_id = agent["restaurant_id"]
    repo.create_sms(
        {
            "restaurant_id": restaurant_id,
            "call_id": None,
            "to_number": from_number,
            "body": body,
            "status": "received",
            "twilio_sid": form.get("MessageSid"),
            "direction": "inbound",
        }
    )

    reply = "Thanks! Reply CANCEL <code> to cancel a reservation, or call us for changes."
    upper = body.upper()
    if upper.startswith("CANCEL"):
        parts = body.split()
        code = parts[1] if len(parts) > 1 else ""
        reservations = repo.list_reservations(restaurant_id)
        match = next(
            (
                r
                for r in reservations
                if r.get("confirmation_code") == code.upper() and r.get("guest_phone") == from_number
            ),
            None,
        )
        if match:
            repo.cancel_reservation(match["id"])
            reply = f"Reservation {code.upper()} cancelled. We hope to see you another time."
        else:
            reply = "We could not find that reservation. Please call us for help."

    return PlainTextResponse(
        f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>',
        media_type="application/xml",
    )
