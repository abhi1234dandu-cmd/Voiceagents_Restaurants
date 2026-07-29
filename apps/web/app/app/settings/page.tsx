"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { Membership, Organization } from "@restaurant-voice/shared-types";

export default function SettingsPage() {
  const [org, setOrg] = useState<Organization | null>(null);
  const [members, setMembers] = useState<Membership[]>([]);

  useEffect(() => {
    apiFetch<Organization>("/v1/orgs/me").then(setOrg);
    apiFetch<Membership[]>("/v1/orgs/me/members").then(setMembers).catch(() => setMembers([]));
  }, []);

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold">Settings & team</h1>
      <section className="mt-8 rounded-lg border border-[var(--line)] bg-white p-5">
        <h2 className="font-semibold">Organization</h2>
        <p className="mt-2 text-sm text-[var(--muted)]">{org?.name}</p>
        <p className="text-sm text-[var(--muted)]">Slug: {org?.slug}</p>
      </section>
      <section className="mt-6">
        <h2 className="font-semibold">Team</h2>
        <ul className="mt-3 divide-y divide-[var(--line)] rounded-lg border border-[var(--line)] bg-white">
          {members.map((m) => (
            <li key={m.id} className="flex justify-between px-4 py-3 text-sm">
              <span className="font-mono">{m.user_id}</span>
              <span className="text-[var(--muted)]">{m.role}</span>
            </li>
          ))}
          {!members.length && <li className="px-4 py-3 text-sm text-[var(--muted)]">No members loaded.</li>}
        </ul>
      </section>
    </div>
  );
}
