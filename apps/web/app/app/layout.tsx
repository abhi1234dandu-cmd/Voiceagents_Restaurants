"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Restaurant } from "@restaurant-voice/shared-types";

const NAV = [
  { href: "/app", label: "Overview" },
  { href: "/app/restaurants", label: "Restaurants" },
  { href: "/app/analytics", label: "Analytics" },
  { href: "/app/billing", label: "Billing" },
  { href: "/app/settings", label: "Settings" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);

  useEffect(() => {
    apiFetch<Restaurant[]>("/v1/restaurants")
      .then((r) => {
        setRestaurants(r);
        if (r[0]) localStorage.setItem("hostline_restaurant_id", r[0].id);
      })
      .catch(() => setRestaurants([]));
  }, []);

  const activeId =
    restaurants[0]?.id ||
    (typeof window !== "undefined" ? localStorage.getItem("hostline_restaurant_id") : null);

  return (
    <div className="flex min-h-screen bg-[var(--linen)]">
      <aside className="flex w-64 flex-col border-r border-[var(--line)] bg-[var(--espresso)] px-4 py-6 text-[var(--linen)]">
        <Link href="/" className="brand px-2 text-2xl font-bold tracking-tight">
          Hostline
        </Link>
        <p className="mt-1 px-2 text-[10px] uppercase tracking-[0.22em] text-[var(--brass)]">
          Restaurant voice
        </p>
        <nav className="mt-10 flex flex-1 flex-col gap-1 text-sm">
          {NAV.map((item) => {
            const active = pathname === item.href || (item.href !== "/app" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-sm px-3 py-2.5 transition ${
                  active
                    ? "bg-[var(--brass)] font-semibold text-[var(--espresso)]"
                    : "text-[var(--linen)]/70 hover:bg-white/5 hover:text-[var(--linen)]"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
          {activeId && (
            <div className="mt-8 border-t border-white/10 pt-5">
              <p className="px-3 text-[10px] uppercase tracking-[0.2em] text-[var(--linen)]/40">
                {restaurants[0]?.name || "Location"}
              </p>
              {[
                ["agent", "Voice agent"],
                ["menu", "Menu"],
                ["faqs", "FAQs"],
                ["reservations", "Reservations"],
                ["calls", "Calls"],
              ].map(([slug, label]) => (
                <Link
                  key={slug}
                  href={`/app/restaurants/${activeId}/${slug}`}
                  className={`mt-1 block rounded-sm px-3 py-2 ${
                    pathname.includes(`/${slug}`)
                      ? "bg-white/10 text-[var(--linen)]"
                      : "text-[var(--linen)]/55 hover:bg-white/5 hover:text-[var(--linen)]"
                  }`}
                >
                  {label}
                </Link>
              ))}
            </div>
          )}
        </nav>
        <Link href="/login" className="mt-4 px-3 text-xs text-[var(--linen)]/40 hover:text-[var(--linen)]">
          Switch account
        </Link>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="border-b border-[var(--line)] bg-[var(--linen-deep)]/50 px-8 py-3 text-xs text-[var(--muted)]">
          Demo mode · in-memory API · ElevenLabs TTS ready when keyed
        </div>
        <div className="px-8 py-8">{children}</div>
      </main>
    </div>
  );
}
