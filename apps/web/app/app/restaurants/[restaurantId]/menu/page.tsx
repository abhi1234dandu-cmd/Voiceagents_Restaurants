"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { MenuItem } from "@restaurant-voice/shared-types";

export default function MenuPage() {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [items, setItems] = useState<MenuItem[]>([]);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("12.00");
  const [category, setCategory] = useState("general");

  function load() {
    apiFetch<MenuItem[]>(`/v1/restaurants/${restaurantId}/menu`).then(setItems);
  }
  useEffect(() => {
    load();
  }, [restaurantId]);

  async function add(e: FormEvent) {
    e.preventDefault();
    await apiFetch(`/v1/restaurants/${restaurantId}/menu`, {
      method: "POST",
      body: JSON.stringify({
        name,
        price_cents: Math.round(parseFloat(price) * 100),
        category,
        description: "",
      }),
    });
    setName("");
    load();
  }

  async function remove(id: string) {
    await apiFetch(`/v1/restaurants/${restaurantId}/menu/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div>
      <h1 className="text-3xl font-bold">Menu</h1>
      <form onSubmit={add} className="mt-6 flex flex-wrap gap-2">
        <input className="rounded-md border border-[var(--line)] px-3 py-2" placeholder="Item" value={name} onChange={(e) => setName(e.target.value)} required />
        <input className="w-24 rounded-md border border-[var(--line)] px-3 py-2" value={price} onChange={(e) => setPrice(e.target.value)} />
        <input className="w-32 rounded-md border border-[var(--line)] px-3 py-2" value={category} onChange={(e) => setCategory(e.target.value)} />
        <button className="rounded-md bg-[var(--ink)] px-4 py-2 text-white">Add</button>
      </form>
      <ul className="mt-8 divide-y divide-[var(--line)] rounded-lg border border-[var(--line)] bg-white">
        {items.map((i) => (
          <li key={i.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="font-medium">{i.name}</p>
              <p className="text-sm text-[var(--muted)]">
                {i.category} · ${(i.price_cents / 100).toFixed(2)}
              </p>
            </div>
            <button type="button" onClick={() => remove(i.id)} className="text-sm text-[var(--danger)]">
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
