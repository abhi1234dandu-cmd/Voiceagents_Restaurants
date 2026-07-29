"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Organization } from "@restaurant-voice/shared-types";

type Plan = { id: string; name: string; price: string; minutes: number | null };

export default function BillingPage() {
  const [org, setOrg] = useState<Organization | null>(null);
  const [usage, setUsage] = useState<Array<{ metric: string; quantity: number }>>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch<Organization>("/v1/orgs/me").then(setOrg);
    apiFetch<Array<{ metric: string; quantity: number }>>("/v1/billing/usage").then(setUsage).catch(() => []);
    apiFetch<Plan[]>("/v1/billing/plans").then(setPlans).catch(() => setPlans([]));
  }, []);

  async function checkout(plan: string) {
    if (plan === "enterprise") {
      setMsg("Enterprise is custom — email sales or use Request quote on /pricing.");
      return;
    }
    const res = await apiFetch<{ url: string }>("/v1/billing/checkout-session", {
      method: "POST",
      body: JSON.stringify({ plan }),
    });
    if (res.url.includes("session=dev")) {
      setMsg(`Dev mode: switched org to ${plan}.`);
      apiFetch<Organization>("/v1/orgs/me").then(setOrg);
      return;
    }
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
    <div className="animate-rise max-w-3xl">
      <h1 className="brand text-4xl font-bold">Billing</h1>
      <p className="mt-2 text-[var(--muted)]">
        Current plan: <strong className="text-[var(--ink)]">{org?.plan ?? "…"}</strong> · {org?.status} · {minutes} voice minutes used
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {plans.map((p) => (
          <div key={p.id} className="border border-[var(--line)] bg-white p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-[var(--olive)]">{p.name}</p>
            <p className="brand mt-2 text-2xl font-bold">{p.price}</p>
            <p className="mt-2 text-sm text-[var(--muted)]">
              {p.minutes ? `Up to ${p.minutes.toLocaleString()} AI minutes` : "Custom / unlimited usage"}
            </p>
            <button
              type="button"
              onClick={() => checkout(p.id)}
              className="btn-primary mt-5 !bg-[var(--espresso)] !py-2.5 !text-[var(--linen)]"
            >
              {p.id === "enterprise" ? "Request quote" : org?.plan === p.id ? "Current plan" : `Choose ${p.name}`}
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <button type="button" onClick={portal} className="rounded-sm border border-[var(--line)] px-4 py-3 text-sm font-semibold">
          Customer portal
        </button>
        <Link href="/pricing" className="rounded-sm border border-[var(--line)] px-4 py-3 text-sm font-semibold">
          View full pricing
        </Link>
      </div>
      {msg && <p className="mt-4 text-sm text-[var(--ok)]">{msg}</p>}
    </div>
  );
}
