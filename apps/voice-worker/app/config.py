from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    api_base_url: str = "http://localhost:8000"
    internal_api_secret: str = "dev-internal-secret-change-me"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    elevenlabs_api_key: str = ""
    elevenlabs_default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_agent_id: str = ""  # reserved; we use OpenAI LLM+tools + ElevenLabs TTS
    sentry_dsn: str = ""
    max_call_seconds: int = 600
    worker_concurrency_hint: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
