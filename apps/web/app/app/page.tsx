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

  return (
    <div>
      <h1 className="text-3xl font-bold">Overview</h1>
      <p className="mt-1 text-[var(--muted)]">{org ? `${org.name} · ${org.plan}` : "Loading…"}</p>
      {error && (
        <p className="mt-4 text-sm text-[var(--danger)]">
          {error} — use{" "}
          <Link href="/login" className="underline">
            login
          </Link>{" "}
          with the local dev token if the API is in-memory.
        </p>
      )}
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {[
          ["Calls", analytics?.total_calls ?? "—"],
          ["Reservations booked", analytics?.reservations_booked ?? "—"],
          ["Voice minutes", analytics?.voice_minutes ?? "—"],
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg border border-[var(--line)] bg-white p-5">
            <p className="text-sm text-[var(--muted)]">{label}</p>
            <p className="mt-2 text-3xl font-bold">{value}</p>
          </div>
        ))}
      </div>
      <section className="mt-10">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Restaurants</h2>
          <Link href="/app/restaurants" className="text-sm font-medium underline">
            Manage
          </Link>
        </div>
        <ul className="mt-4 space-y-2">
          {restaurants.map((r) => (
            <li key={r.id}>
              <Link
                href={`/app/restaurants/${r.id}/agent`}
                className="block rounded-lg border border-[var(--line)] bg-white px-4 py-3 hover:border-[var(--ink)]"
              >
                <span className="font-medium">{r.name}</span>
                <span className="ml-2 text-sm text-[var(--muted)]">{r.status}</span>
              </Link>
            </li>
          ))}
          {!restaurants.length && !error && <li className="text-[var(--muted)]">No restaurants yet.</li>}
        </ul>
      </section>
    </div>
  );
}
