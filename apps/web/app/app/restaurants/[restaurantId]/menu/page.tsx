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
      body: JSON.stringify({ name, price_cents: Math.round(parseFloat(price) * 100), category, description: "" }),
    });
    setName("");
    load();
  }

  async function remove(id: string) {
    await apiFetch(`/v1/restaurants/${restaurantId}/menu/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div className="animate-rise">
      <h1 className="brand text-4xl font-bold">Menu</h1>
      <form onSubmit={add} className="mt-8 flex flex-wrap gap-2">
        <input className="field max-w-xs" placeholder="Item" value={name} onChange={(e) => setName(e.target.value)} required />
        <input className="field w-24" value={price} onChange={(e) => setPrice(e.target.value)} />
        <input className="field w-32" value={category} onChange={(e) => setCategory(e.target.value)} />
        <button className="btn-primary !bg-[var(--espresso)] !text-[var(--linen)]">Add</button>
      </form>
      <ul className="mt-8 divide-y divide-[var(--line)] border border-[var(--line)] bg-white">
        {items.map((i) => (
          <li key={i.id} className="flex items-center justify-between px-4 py-3">
            <div>
              <p className="font-semibold">{i.name}</p>
              <p className="text-sm text-[var(--muted)]">{i.category} · ${(i.price_cents / 100).toFixed(2)}</p>
            </div>
            <button type="button" onClick={() => remove(i.id)} className="text-sm text-[var(--danger)]">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
