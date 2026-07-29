# API keys & secrets

Copy `.env.example` → `.env`, then also into `apps/api/.env`, `apps/voice-worker/.env`, and public keys into `apps/web/.env.local`.

| Service | Variables | Where used |
|---|---|---|
| **Supabase** | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET` | Web auth + API DB (leave blank for local in-memory demo) |
| **ElevenLabs** | `ELEVENLABS_API_KEY`, `ELEVENLABS_DEFAULT_VOICE_ID` | `apps/voice-worker` TTS |
| **OpenAI** | `OPENAI_API_KEY`, `OPENAI_MODEL` | `apps/voice-worker` LLM/tools |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | `apps/api` numbers/SMS/voice webhooks |
| **Stripe** | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_STARTER`, `STRIPE_PRICE_ID_PROFESSIONAL`, `STRIPE_PRICE_ID_PREMIUM`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `apps/api` billing + `apps/web` |
| **App URLs** | `NEXT_PUBLIC_APP_URL`, `API_BASE_URL`, `NEXT_PUBLIC_API_URL`, `VOICE_WORKER_WS_URL`, `INTERNAL_API_SECRET` | Local/prod wiring |
| **Admin** | `PLATFORM_ADMIN_USER_IDS` | Comma-separated Supabase user UUIDs |

Voice worker WebSocket URL must be publicly reachable (`wss://…`) for real Twilio calls.
