from typing import Any, Optional

from app.config import Settings


class TwilioService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    @property
    def client(self):
        if self._client is None:
            if not self.settings.twilio_account_sid or not self.settings.twilio_auth_token:
                return None
            from twilio.rest import Client

            self._client = Client(self.settings.twilio_account_sid, self.settings.twilio_auth_token)
        return self._client

    def provision_number(self, area_code: Optional[str] = None) -> dict[str, Any]:
        if not self.client:
            # Dev mock number
            return {
                "sid": "PNdevmock0001",
                "phone_number": "+15555550100",
                "mock": True,
            }
        params: dict[str, Any] = {"voice_enabled": True, "sms_enabled": True}
        if area_code:
            params["area_code"] = area_code
        numbers = self.client.available_phone_numbers("US").local.list(**params, limit=1)
        if not numbers:
            raise RuntimeError("No Twilio numbers available")
        purchased = self.client.incoming_phone_numbers.create(
            phone_number=numbers[0].phone_number,
            voice_url=f"{self.settings.api_base_url}/webhooks/twilio/voice",
            voice_method="POST",
            status_callback=f"{self.settings.api_base_url}/webhooks/twilio/status",
            sms_url=f"{self.settings.api_base_url}/webhooks/twilio/sms",
        )
        return {"sid": purchased.sid, "phone_number": purchased.phone_number, "mock": False}

    def send_sms(self, from_number: str, to_number: str, body: str) -> dict[str, Any]:
        if not self.client:
            return {"sid": "SMdevmock", "status": "queued", "mock": True}
        msg = self.client.messages.create(from_=from_number, to=to_number, body=body)
        return {"sid": msg.sid, "status": msg.status, "mock": False}

    def validate_signature(self, url: str, params: dict[str, Any], signature: str) -> bool:
        if not self.settings.twilio_auth_token:
            return True  # allow in local/dev
        from twilio.request_validator import RequestValidator

        validator = RequestValidator(self.settings.twilio_auth_token)
        return validator.validate(url, params, signature)
