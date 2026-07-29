"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Restaurant } from "@restaurant-voice/shared-types";

export default function RestaurantsPage() {
  const [items, setItems] = useState<Restaurant[]>([]);
  const [name, setName] = useState("");

  function load() {
    apiFetch<Restaurant[]>("/v1/restaurants").then(setItems).catch(() => setItems([]));
  }

  useEffect(() => {
    load();
  }, []);

  async function create(e: FormEvent) {
    e.preventDefault();
    const r = await apiFetch<Restaurant>("/v1/restaurants", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    localStorage.setItem("hostline_restaurant_id", r.id);
    setName("");
    load();
  }

  return (
    <div className="animate-rise">
      <h1 className="brand text-4xl font-bold">Restaurants</h1>
      <p className="mt-2 text-[var(--muted)]">Locations with their own number and ElevenLabs voice.</p>
      <form onSubmit={create} className="mt-8 flex flex-wrap gap-2">
        <input className="field max-w-md flex-1" placeholder="New restaurant name" value={name} onChange={(e) => setName(e.target.value)} required />
        <button type="submit" className="btn-primary !bg-[var(--espresso)] !text-[var(--linen)]">Add</button>
      </form>
      <ul className="mt-8 space-y-3">
        {items.map((r) => (
          <li key={r.id} className="flex items-center justify-between border border-[var(--line)] bg-white px-5 py-4">
            <div>
              <p className="font-semibold">{r.name}</p>
              <p className="text-sm text-[var(--muted)]">{r.phone_e164 || "No number"} · {r.timezone}</p>
            </div>
            <Link href={`/app/restaurants/${r.id}/agent`} className="text-sm font-semibold text-[var(--olive)] underline">
              Configure
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
