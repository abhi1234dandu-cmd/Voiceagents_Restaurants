"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
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
    <main className="min-h-screen bg-[var(--linen)] px-4 py-16">
      <div className="mx-auto max-w-lg animate-rise">
        <Link href="/" className="brand text-2xl font-bold">Hostline</Link>
        <h1 className="brand mt-8 text-4xl font-bold">Set up your first restaurant</h1>
        <p className="mt-2 text-[var(--muted)]">We&apos;ll create an ElevenLabs-powered voice agent next.</p>
        <form onSubmit={onSubmit} className="mt-8 space-y-4">
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Organization name</span>
            <input className="field" value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Demo Bistro Org" />
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Restaurant name</span>
            <input className="field" value={restaurantName} onChange={(e) => setRestaurantName(e.target.value)} required />
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Staff transfer number</span>
            <input className="field" value={transfer} onChange={(e) => setTransfer(e.target.value)} placeholder="+15555550999" />
          </label>
          {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Creating…" : "Continue to agent"}
          </button>
        </form>
      </div>
    </main>
  );
}
