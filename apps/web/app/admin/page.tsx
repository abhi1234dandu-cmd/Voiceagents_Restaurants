"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

type AdminOrg = {
  id: string;
  name: string;
  plan: string;
  status: string;
  voice_minutes: number;
};

export default function AdminPage() {
  const [orgs, setOrgs] = useState<AdminOrg[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<AdminOrg[]>("/admin/orgs")
      .then(setOrgs)
      .catch((e) => setError(e.message));
  }, []);

  async function suspend(id: string) {
    await apiFetch(`/admin/orgs/${id}/suspend`, { method: "POST" });
    setOrgs((prev) => prev.map((o) => (o.id === id ? { ...o, status: "suspended" } : o)));
  }

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-10">
      <Link href="/app" className="brand text-xl font-extrabold">
        Hostline
      </Link>
      <h1 className="mt-6 text-3xl font-bold">Platform admin</h1>
      {error && <p className="mt-4 text-sm text-[var(--danger)]">{error}</p>}
      <table className="mt-8 w-full text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--line)] text-[var(--muted)]">
            <th className="py-2">Org</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Minutes</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {orgs.map((o) => (
            <tr key={o.id} className="border-b border-[var(--line)]">
              <td className="py-3">{o.name}</td>
              <td>{o.plan}</td>
              <td>{o.status}</td>
              <td>{o.voice_minutes}</td>
              <td>
                <button type="button" onClick={() => suspend(o.id)} className="text-[var(--danger)]">
                  Suspend
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
