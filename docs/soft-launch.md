# Soft launch checklist

- [ ] Merge PR #1 after CI green
- [ ] Create Supabase project; apply `supabase/migrations`
- [ ] Fill keys per [api-keys.md](./api-keys.md)
- [ ] Deploy `apps/web` → Vercel; `apps/api` + `apps/voice-worker` → Railway
- [ ] Set `VOICE_WORKER_WS_URL` to public `wss://…/media`
- [ ] Twilio number voice webhook → `https://<api>/webhooks/twilio/voice`
- [ ] Stripe webhook → `https://<api>/v1/billing/webhooks/stripe`
- [ ] Create Stripe prices for Starter / Professional / Premium; paste IDs into env
- [ ] Demo walkthrough: onboard → agent voice_id → FAQ/menu → test reservation
- [ ] Pilot 1–3 restaurants; watch Sentry + call outcomes
