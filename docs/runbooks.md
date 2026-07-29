# Runbooks

## Local development

1. Copy `.env.example` → `.env` and set secrets (ElevenLabs, OpenAI, Twilio, Stripe, Supabase).
2. Apply SQL: `supabase/migrations/20260729000000_init.sql` then optionally `supabase/policies/rls_extra.sql` and `supabase/seed.sql`.
3. API: `cd apps/api && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
4. Voice worker: `cd apps/voice-worker && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8001`
5. Web: `npm install && npm run dev:web`
6. Dev auth header: `Authorization: Bearer dev:<user_id>:<org_id>:owner`

## Twilio Media Streams

- Point the Twilio number voice webhook to `https://<api>/webhooks/twilio/voice`.
- Set `VOICE_WORKER_WS_URL` to `wss://<worker>/media`.
- Confirm `voice_id` is set on the restaurant agent (ElevenLabs voice).

## ElevenLabs TTS outage

- Spoken audio always goes through ElevenLabs. If TTS fails mid-call, the worker may transfer after repeated LLM failures.
- Verify `ELEVENLABS_API_KEY` and that `voice_agents.voice_id` exists in the ElevenLabs account.
- Without a key (dev), silence frames are streamed so the protocol still works.

## Stripe billing

- Configure webhook → `POST /v1/billing/webhooks/stripe` for `checkout.session.completed`, `customer.subscription.*`, `invoice.payment_failed`.
- Failed payment sets org `status=past_due`, `plan=free`.

## Recording retention

- Job: `POST /internal/jobs/retention/recordings` (internal secret) honors `RECORDING_RETENTION_DAYS` (default 90).

## Scaling voice workers

- Hit `/metrics` — `utilization = active_streams / WORKER_CONCURRENCY_HINT`.
- Scale Railway replicas when utilization > ~0.7.

## Common failures

| Symptom | Check |
|---------|--------|
| "number not configured" | Agent `twilio_phone_e164` matches Twilio To |
| 401 on API | JWT secret / `dev:` token format |
| Tools 401 | `INTERNAL_API_SECRET` mismatch between API and worker |
| No speech | ElevenLabs key / voice_id / Accept audio format |
