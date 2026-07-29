"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Organization } from "@restaurant-voice/shared-types";

export default function BillingPage() {
  const [org, setOrg] = useState<Organization | null>(null);
  const [usage, setUsage] = useState<Array<{ metric: string; quantity: number }>>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch<Organization>("/v1/orgs/me").then(setOrg);
    apiFetch<Array<{ metric: string; quantity: number }>>("/v1/billing/usage").then(setUsage).catch(() => []);
  }, []);

  async function checkout() {
    const res = await apiFetch<{ url: string }>("/v1/billing/checkout-session", { method: "POST" });
    window.location.href = res.url;
  }

  async function portal() {
    try {
      const res = await apiFetch<{ url: string }>("/v1/billing/portal", { method: "POST" });
      window.location.href = res.url;
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Portal unavailable");
    }
  }

  const minutes = usage.filter((u) => u.metric === "voice_minutes").reduce((s, u) => s + Number(u.quantity), 0);

  return (
    <div className="animate-rise max-w-xl">
      <h1 className="brand text-4xl font-bold">Billing</h1>
      <p className="mt-2 text-[var(--muted)]">
        Plan: <strong className="text-[var(--ink)]">{org?.plan ?? "…"}</strong> · Status: {org?.status}
      </p>
      <p className="mt-4">Voice minutes used: {minutes}</p>
      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" onClick={checkout} className="btn-primary !bg-[var(--espresso)] !text-[var(--linen)]">
          Upgrade / Checkout
        </button>
        <button type="button" onClick={portal} className="rounded-sm border border-[var(--line)] px-4 py-3 text-sm font-semibold">
          Customer portal
        </button>
      </div>
      {msg && <p className="mt-4 text-sm text-[var(--danger)]">{msg}</p>}
    </div>
  );
}
