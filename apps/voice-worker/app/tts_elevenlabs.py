import base64
from typing import AsyncIterator, Optional

import httpx

from app.config import Settings


class ElevenLabsTTS:
    def __init__(self, settings: Settings, voice_id: Optional[str] = None):
        self.settings = settings
        self.voice_id = voice_id or settings.elevenlabs_default_voice_id

    async def synthesize_mulaw_base64(self, text: str) -> AsyncIterator[str]:
        """Yield base64 mulaw frames for Twilio Media Streams."""
        if not text:
            return
        if not self.settings.elevenlabs_api_key:
            # Dev: silence / skip — stream layer will still send mark events
            yield base64.b64encode(b"\xff" * 160).decode("ascii")
            return

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
        headers = {
            "xi-api-key": self.settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/basic",
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                buffer = b""
                async for chunk in resp.aiter_bytes():
                    buffer += chunk
                    while len(buffer) >= 160:
                        frame = buffer[:160]
                        buffer = buffer[160:]
                        yield base64.b64encode(frame).decode("ascii")
                if buffer:
                    yield base64.b64encode(buffer).decode("ascii")
