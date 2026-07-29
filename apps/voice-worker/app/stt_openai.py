"""OpenAI STT helpers. Production can swap to Realtime API; MVP uses text simulation + Whisper-ready stubs."""

from typing import Optional

from app.config import Settings


class SpeechToText:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    @property
    def client(self):
        if self._client is None and self.settings.openai_api_key:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.settings.openai_api_key)
        return self._client

    def transcribe_mulaw(self, audio_bytes: bytes) -> str:
        """Transcribe mulaw audio. Falls back to empty if no key / empty buffer."""
        if not audio_bytes or not self.client:
            return ""
        # Convert would happen here; for MVP we accept that stream.py may pass text events in test mode
        try:
            # Placeholder: real impl writes temp wav and calls whisper
            return ""
        except Exception:
            return ""
