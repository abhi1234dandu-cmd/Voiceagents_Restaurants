"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { AnalyticsSummary } from "@restaurant-voice/shared-types";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  useEffect(() => {
    apiFetch<AnalyticsSummary>("/v1/analytics/summary").then(setData);
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold">Analytics</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Total calls", data?.total_calls],
          ["Answered", data?.answered_calls],
          ["Reservations", data?.reservations_booked],
          ["Transfers", data?.transfers],
        ].map(([label, value]) => (
          <div key={String(label)} className="rounded-lg border border-[var(--line)] bg-white p-5">
            <p className="text-sm text-[var(--muted)]">{label}</p>
            <p className="mt-2 text-3xl font-bold">{value ?? "—"}</p>
          </div>
        ))}
      </div>
      <p className="mt-6 text-[var(--muted)]">Voice minutes: {data?.voice_minutes ?? "—"}</p>
    </div>
  );
}
