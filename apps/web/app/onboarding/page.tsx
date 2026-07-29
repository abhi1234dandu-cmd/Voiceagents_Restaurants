"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { Restaurant } from "@restaurant-voice/shared-types";

export default function OnboardingPage() {
  const router = useRouter();
  const [orgName, setOrgName] = useState("");
  const [restaurantName, setRestaurantName] = useState("");
  const [transfer, setTransfer] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await apiFetch("/v1/orgs/bootstrap", {
        method: "POST",
        body: JSON.stringify({ name: orgName || "My Restaurant Group" }),
      });
      const restaurant = await apiFetch<Restaurant>("/v1/restaurants", {
        method: "POST",
        body: JSON.stringify({
          name: restaurantName,
          transfer_number_e164: transfer || null,
          hours_json: { "mon-sun": "11:00-22:00" },
        }),
      });
      localStorage.setItem("hostline_restaurant_id", restaurant.id);
      router.push(`/app/restaurants/${restaurant.id}/agent`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Onboarding failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center px-4 py-12">
      <p className="brand text-xl font-extrabold">Hostline</p>
      <h1 className="mt-4 text-3xl font-bold">Set up your first restaurant</h1>
      <p className="mt-2 text-[var(--muted)]">We&apos;ll create an ElevenLabs-powered voice agent you can tune next.</p>
      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        <label className="block text-sm">
          Organization name
          <input
            className="mt-1 w-full rounded-md border border-[var(--line)] px-3 py-2"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            placeholder="Demo Bistro Org"
          />
        </label>
        <label className="block text-sm">
          Restaurant name
          <input
            className="mt-1 w-full rounded-md border border-[var(--line)] px-3 py-2"
            value={restaurantName}
            onChange={(e) => setRestaurantName(e.target.value)}
            required
          />
        </label>
        <label className="block text-sm">
          Staff transfer number (E.164)
          <input
            className="mt-1 w-full rounded-md border border-[var(--line)] px-3 py-2"
            value={transfer}
            onChange={(e) => setTransfer(e.target.value)}
            placeholder="+15555550999"
          />
        </label>
        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
        <button type="submit" disabled={loading} className="w-full rounded-md bg-[var(--ink)] py-2.5 font-semibold text-white">
          {loading ? "Creating…" : "Continue to agent settings"}
        </button>
      </form>
    </main>
  );
}
