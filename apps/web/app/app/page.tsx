"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import type { AnalyticsSummary, Organization, Restaurant } from "@restaurant-voice/shared-types";

export default function AppHomePage() {
  const [org, setOrg] = useState<Organization | null>(null);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch<Organization>("/v1/orgs/me"),
      apiFetch<Restaurant[]>("/v1/restaurants"),
      apiFetch<AnalyticsSummary>("/v1/analytics/summary"),
    ])
      .then(([o, r, a]) => {
        setOrg(o);
        setRestaurants(r);
        setAnalytics(a);
        if (r[0]) localStorage.setItem("hostline_restaurant_id", r[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  const rid = restaurants[0]?.id;

  return (
    <div className="animate-rise">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--olive)]">Tonight&apos;s floor</p>
      <h1 className="brand mt-2 text-4xl font-bold text-[var(--ink)]">Overview</h1>
      <p className="mt-2 text-[var(--muted)]">
        {org ? `${org.name} · ${org.plan} plan` : "Loading your dining room…"}
      </p>

      {error && (
        <p className="mt-4 rounded-sm border border-[var(--danger)]/30 bg-white px-4 py-3 text-sm text-[var(--danger)]">
          {error} — go to{" "}
          <Link href="/login" className="underline">
            login
          </Link>{" "}
          and click <strong>Enter demo dashboard</strong>.
        </p>
      )}

      <div className="mt-10 grid gap-4 sm:grid-cols-3">
        {[
          ["Calls answered", analytics?.total_calls ?? "—", "Inbound voice"],
          ["Tables booked", analytics?.reservations_booked ?? "—", "From the agent"],
          ["Voice minutes", analytics?.voice_minutes ?? "—", "Usage this period"],
        ].map(([label, value, hint]) => (
          <div key={label} className="panel">
            <p className="text-xs uppercase tracking-wider text-[var(--muted)]">{label}</p>
            <p className="brand mt-3 text-4xl font-bold text-[var(--ink)]">{value}</p>
            <p className="mt-2 text-xs text-[var(--muted)]">{hint}</p>
          </div>
        ))}
      </div>

      <section className="mt-12">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="brand text-2xl font-bold">Your restaurants</h2>
            <p className="mt-1 text-sm text-[var(--muted)]">Numbers, agents, and bookings live here.</p>
          </div>
          <Link href="/app/restaurants" className="text-sm font-semibold text-[var(--olive)] underline">
            Manage all
          </Link>
        </div>
        <ul className="mt-6 space-y-3">
          {restaurants.map((r) => (
            <li key={r.id}>
              <Link
                href={`/app/restaurants/${r.id}/agent`}
                className="flex items-center justify-between gap-4 border border-[var(--line)] bg-white px-5 py-4 transition hover:border-[var(--olive)]"
              >
                <div>
                  <p className="font-semibold text-[var(--ink)]">{r.name}</p>
                  <p className="mt-1 text-sm text-[var(--muted)]">
                    {r.phone_e164 || "No number yet"} · {r.status}
                  </p>
                </div>
                <span className="text-sm font-medium text-[var(--brass-deep)]">Open agent →</span>
              </Link>
            </li>
          ))}
          {!restaurants.length && !error && (
            <li className="text-[var(--muted)]">No restaurants yet — finish onboarding.</li>
          )}
        </ul>
      </section>

      {rid && (
        <section className="mt-12 grid gap-3 sm:grid-cols-3">
          {[
            [`/app/restaurants/${rid}/calls`, "Review calls"],
            [`/app/restaurants/${rid}/reservations`, "Reservations"],
            [`/app/restaurants/${rid}/menu`, "Edit menu"],
          ].map(([href, label]) => (
            <Link
              key={href}
              href={href}
              className="border border-[var(--line)] bg-[var(--espresso)] px-4 py-4 text-sm font-medium text-[var(--linen)] transition hover:bg-[var(--espresso-soft)]"
            >
              {label}
            </Link>
          ))}
        </section>
      )}
    </div>
  );
}
