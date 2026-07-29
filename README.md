# Restaurant Voice SaaS

Multi-tenant AI voice agent platform for restaurants.

## Stack

- **Web**: Next.js 15, TypeScript, Tailwind (Vercel)
- **API**: FastAPI (Railway)
- **Voice Worker**: FastAPI WebSocket Media Streams (Railway)
- **DB/Auth/Storage**: Supabase (PostgreSQL + RLS)
- **Voice/AI**: Twilio, OpenAI, ElevenLabs
- **Billing**: Stripe

## Quick start

### Prerequisites

- Node 20+
- Python 3.11+
- Supabase project (or local CLI)
- Twilio / OpenAI / ElevenLabs / Stripe test credentials

### Setup

```bash
cp .env.example .env
npm install

# API
cd apps/api && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Voice worker (separate terminal)
cd apps/voice-worker && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Web
npm run dev:web
```

### Docker

```bash
docker compose -f infra/docker-compose.yml up --build
```

### Migrations

```bash
npx supabase db push
# or apply supabase/migrations/*.sql in the SQL editor
```

## Voice

Spoken audio is **ElevenLabs TTS** only (`apps/voice-worker/app/tts_elevenlabs.py`). Orchestration is OpenAI LLM + internal tools — not ElevenLabs Conversational AI — so reservations/SMS/transfer stay on our API. Set `ELEVENLABS_API_KEY`, `ELEVENLABS_DEFAULT_VOICE_ID`, and per-restaurant `voice_id` in Agent settings. See [architecture](docs/architecture.md).
