"""
# Restaurant Voice SaaS — Architecture

## Services

| Service | Runtime | Role |
|---------|---------|------|
| `apps/web` | Next.js 15 (Vercel) | Marketing, auth, dashboard |
| `apps/api` | FastAPI (Railway) | REST API, Twilio/Stripe webhooks, tool endpoints |
| `apps/voice-worker` | FastAPI WS (Railway) | Twilio Media Streams, STT/LLM/TTS loop |
| Supabase | Postgres + Auth + Storage | Multi-tenant data + RLS |

## Call path

```
Caller → Twilio number → API /webhooks/twilio/voice (TwiML <Stream>)
      → voice-worker /media WebSocket
      → STT (OpenAI Whisper)
      → LLM + tools (OpenAI chat completions)
      → TTS (ElevenLabs streaming → μ-law frames)
      → Twilio plays audio to caller
```

Tools hit `API /internal/tools/*` with `X-Internal-Secret` (hours, FAQ, menu, reservations, SMS, transfer).

## Voice / ElevenLabs

**Shipped path:** OpenAI LLM + internal tools + **ElevenLabs TTS** (required for all spoken output).

- Per-restaurant `voice_agents.voice_id` is passed as a Twilio Stream parameter and used by `ElevenLabsTTS`.
- Fallback when no key: short silence frames (tests/dev).
- `ELEVENLABS_AGENT_ID` is reserved for future ElevenLabs Conversational AI. We do **not** use Conversational AI for orchestration today because restaurant tools (reservations, SMS, transfer) live on our API and need tight control.

## Multi-tenancy

- Orgs → memberships → restaurants → agent/menu/faqs/calls.
- Dashboard auth: Supabase JWT (or `dev:<user_id>:<org_id>:<role>` when JWT secret unset).
- API uses service role; browser uses anon key + RLS.

## Billing

Stripe Checkout + Customer Portal. Webhooks upsert `billing_subscriptions` and update org `plan`/`status`.

## Observability

`/health` on API and worker; worker `/metrics` exposes active Media Stream count for autoscaling. Optional Sentry.
"""
