"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { Reservation } from "@restaurant-voice/shared-types";

export default function ReservationsPage() {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [rows, setRows] = useState<Reservation[]>([]);
  const [guestName, setGuestName] = useState("");
  const [guestPhone, setGuestPhone] = useState("");
  const [partySize, setPartySize] = useState(2);
  const [startsAt, setStartsAt] = useState("");

  function load() {
    apiFetch<Reservation[]>(`/v1/restaurants/${restaurantId}/reservations`).then(setRows);
  }
  useEffect(() => {
    load();
  }, [restaurantId]);

  async function create(e: FormEvent) {
    e.preventDefault();
    await apiFetch(`/v1/restaurants/${restaurantId}/reservations`, {
      method: "POST",
      body: JSON.stringify({
        guest_name: guestName,
        guest_phone: guestPhone,
        party_size: partySize,
        starts_at: new Date(startsAt).toISOString(),
      }),
    });
    load();
  }

  async function cancel(id: string) {
    await apiFetch(`/v1/reservations/${id}/cancel`, { method: "POST" });
    load();
  }

  return (
    <div>
      <h1 className="text-3xl font-bold">Reservations</h1>
      <form onSubmit={create} className="mt-6 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        <input className="rounded-md border border-[var(--line)] px-3 py-2" placeholder="Guest name" value={guestName} onChange={(e) => setGuestName(e.target.value)} required />
        <input className="rounded-md border border-[var(--line)] px-3 py-2" placeholder="Phone" value={guestPhone} onChange={(e) => setGuestPhone(e.target.value)} required />
        <input className="rounded-md border border-[var(--line)] px-3 py-2" type="number" min={1} max={20} value={partySize} onChange={(e) => setPartySize(Number(e.target.value))} />
        <input className="rounded-md border border-[var(--line)] px-3 py-2" type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} required />
        <button className="rounded-md bg-[var(--ink)] px-4 py-2 text-white">Book</button>
      </form>
      <table className="mt-8 w-full text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--line)] text-[var(--muted)]">
            <th className="py-2">Guest</th>
            <th>Party</th>
            <th>When</th>
            <th>Code</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-b border-[var(--line)]">
              <td className="py-3">{r.guest_name}</td>
              <td>{r.party_size}</td>
              <td>{new Date(r.starts_at).toLocaleString()}</td>
              <td className="font-mono">{r.confirmation_code}</td>
              <td>{r.status}</td>
              <td>
                {r.status !== "cancelled" && (
                  <button type="button" onClick={() => cancel(r.id)} className="text-[var(--danger)]">
                    Cancel
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
