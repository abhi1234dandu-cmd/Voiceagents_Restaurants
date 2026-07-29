from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    api_base_url: str = "http://localhost:8000"
    voice_worker_ws_url: str = "ws://localhost:8001/media"
    internal_api_secret: str = "dev-internal-secret-change-me"
    app_url: str = "http://localhost:3000"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    database_url: str = ""

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_address_sid: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    elevenlabs_api_key: str = ""
    elevenlabs_default_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_agent_id: str = ""  # optional; Conversational AI not used for tool calls

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""  # legacy / default (starter)
    stripe_price_id_starter: str = ""
    stripe_price_id_professional: str = ""
    stripe_price_id_premium: str = ""

    sentry_dsn: str = ""
    platform_admin_user_ids: str = ""
    recording_retention_days: int = 90

    @property
    def admin_ids(self) -> set[str]:
        return {x.strip() for x in self.platform_admin_user_ids.split(",") if x.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
