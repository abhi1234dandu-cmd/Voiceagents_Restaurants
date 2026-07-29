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
  { href: "/admin", label: "Admin" },
];

export default function AppLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);

  useEffect(() => {
    apiFetch<Restaurant[]>("/v1/restaurants")
      .then(setRestaurants)
      .catch(() => setRestaurants([]));
  }, []);

  const activeId =
    restaurants[0]?.id ||
    (typeof window !== "undefined" ? localStorage.getItem("hostline_restaurant_id") : null);

  return (
    <div className="flex min-h-screen bg-[var(--paper)]">
      <aside className="flex w-60 flex-col border-r border-[var(--line)] bg-white px-4 py-6">
        <Link href="/" className="brand px-2 text-xl font-extrabold">
          Hostline
        </Link>
        <nav className="mt-8 flex flex-1 flex-col gap-1 text-sm">
          {NAV.map((item) => {
            const active = pathname === item.href || (item.href !== "/app" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-md px-3 py-2 ${active ? "bg-[var(--ink)] text-white" : "text-[var(--muted)] hover:bg-[var(--mist)]"}`}
              >
                {item.label}
              </Link>
            );
          })}
          {activeId && (
            <div className="mt-6 border-t border-[var(--line)] pt-4">
              <p className="px-3 text-xs uppercase tracking-wide text-[var(--muted)]">Restaurant</p>
              {[
                ["agent", "Agent"],
                ["menu", "Menu"],
                ["faqs", "FAQs"],
                ["reservations", "Reservations"],
                ["calls", "Calls"],
              ].map(([slug, label]) => (
                <Link
                  key={slug}
                  href={`/app/restaurants/${activeId}/${slug}`}
                  className={`mt-1 block rounded-md px-3 py-2 ${
                    pathname.includes(`/${slug}`) ? "bg-[var(--mist)] text-[var(--ink)]" : "text-[var(--muted)] hover:bg-[var(--mist)]"
                  }`}
                >
                  {label}
                </Link>
              ))}
            </div>
          )}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto px-8 py-8">{children}</main>
    </div>
  );
}
