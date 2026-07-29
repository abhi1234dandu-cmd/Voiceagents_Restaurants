"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { VoiceAgent } from "@restaurant-voice/shared-types";

export default function AgentPage() {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [agent, setAgent] = useState<VoiceAgent | null>(null);
  const [voiceId, setVoiceId] = useState("");
  const [greeting, setGreeting] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [active, setActive] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch<VoiceAgent>(`/v1/restaurants/${restaurantId}/agent`).then((a) => {
      setAgent(a);
      setVoiceId(a.voice_id);
      setGreeting(a.greeting);
      setSystemPrompt(a.system_prompt);
      setActive(a.active);
    });
  }, [restaurantId]);

  async function save(e: FormEvent) {
    e.preventDefault();
    const updated = await apiFetch<VoiceAgent>(`/v1/restaurants/${restaurantId}/agent`, {
      method: "PATCH",
      body: JSON.stringify({ voice_id: voiceId, greeting, system_prompt: systemPrompt, active }),
    });
    setAgent(updated);
    setMsg("Saved — ElevenLabs will use this voice_id on the next call.");
  }

  async function provision() {
    const res = await apiFetch<{ phone_e164: string }>(`/v1/restaurants/${restaurantId}/twilio/provision-number`, {
      method: "POST",
    });
    setMsg(`Provisioned ${res.phone_e164}`);
  }

  if (!agent) return <p className="text-[var(--muted)]">Loading agent…</p>;

  return (
    <div className="animate-rise max-w-2xl">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--olive)]">ElevenLabs</p>
      <h1 className="brand mt-2 text-4xl font-bold">Voice agent</h1>
      <p className="mt-2 text-[var(--muted)]">
        Speech out is always ElevenLabs TTS. Number: {agent.twilio_phone_e164 || "not provisioned"}
      </p>
      <form onSubmit={save} className="mt-8 space-y-4">
        <label className="block text-sm">
          <span className="text-[var(--muted)]">ElevenLabs voice ID</span>
          <input className="field font-mono text-sm" value={voiceId} onChange={(e) => setVoiceId(e.target.value)} required />
        </label>
        <label className="block text-sm">
          <span className="text-[var(--muted)]">Greeting</span>
          <textarea className="field" rows={2} value={greeting} onChange={(e) => setGreeting(e.target.value)} />
        </label>
        <label className="block text-sm">
          <span className="text-[var(--muted)]">Extra system prompt</span>
          <textarea className="field" rows={4} value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)} />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />
          Agent active
        </label>
        <div className="flex flex-wrap gap-3">
          <button type="submit" className="btn-primary">Save agent</button>
          <button type="button" onClick={provision} className="rounded-sm border border-[var(--line)] px-4 py-3 text-sm font-semibold hover:bg-white">
            Provision Twilio number
          </button>
        </div>
      </form>
      {msg && <p className="mt-4 text-sm text-[var(--ok)]">{msg}</p>}
    </div>
  );
}
