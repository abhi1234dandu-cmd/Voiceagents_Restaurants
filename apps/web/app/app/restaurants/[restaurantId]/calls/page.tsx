"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { Call, CallTurn } from "@restaurant-voice/shared-types";

export default function CallsPage() {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [calls, setCalls] = useState<Call[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [turns, setTurns] = useState<CallTurn[]>([]);

  useEffect(() => {
    apiFetch<Call[]>(`/v1/restaurants/${restaurantId}/calls`).then(setCalls);
  }, [restaurantId]);

  useEffect(() => {
    if (!selected) return;
    apiFetch<CallTurn[]>(`/v1/calls/${selected}/turns`).then(setTurns);
  }, [selected]);

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div>
        <h1 className="text-3xl font-bold">Calls</h1>
        <ul className="mt-6 space-y-2">
          {calls.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => setSelected(c.id)}
                className={`w-full rounded-lg border px-4 py-3 text-left ${selected === c.id ? "border-[var(--ink)] bg-white" : "border-[var(--line)] bg-white"}`}
              >
                <p className="font-medium">{c.from_number || "Unknown"}</p>
                <p className="text-sm text-[var(--muted)]">
                  {c.outcome || "—"} · {c.duration_sec ?? 0}s
                </p>
              </button>
            </li>
          ))}
          {!calls.length && <li className="text-[var(--muted)]">No calls yet.</li>}
        </ul>
      </div>
      <div>
        <h2 className="text-xl font-semibold">Transcript</h2>
        <div className="mt-4 space-y-3 rounded-lg border border-[var(--line)] bg-white p-4">
          {turns.map((t) => (
            <div key={t.id}>
              <p className="text-xs uppercase text-[var(--muted)]">{t.role}</p>
              <p>{t.content}</p>
            </div>
          ))}
          {selected && !turns.length && <p className="text-[var(--muted)]">No turns logged.</p>}
          {!selected && <p className="text-[var(--muted)]">Select a call.</p>}
        </div>
      </div>
    </div>
  );
}
