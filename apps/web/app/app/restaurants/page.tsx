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
    <div>
      <h1 className="text-3xl font-bold">Restaurants</h1>
      <form onSubmit={create} className="mt-6 flex gap-2">
        <input
          className="flex-1 rounded-md border border-[var(--line)] px-3 py-2"
          placeholder="New restaurant name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <button type="submit" className="rounded-md bg-[var(--ink)] px-4 py-2 text-white">
          Add
        </button>
      </form>
      <ul className="mt-8 space-y-2">
        {items.map((r) => (
          <li key={r.id} className="flex items-center justify-between rounded-lg border border-[var(--line)] bg-white px-4 py-3">
            <div>
              <p className="font-medium">{r.name}</p>
              <p className="text-sm text-[var(--muted)]">{r.phone_e164 || "No number"} · {r.timezone}</p>
            </div>
            <Link href={`/app/restaurants/${r.id}/agent`} className="text-sm font-medium underline">
              Configure
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
