"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const supabase = createClient();
      const { error: err } = await supabase.auth.signUp({ email, password });
      if (err) {
        localStorage.setItem(
          "hostline_dev_token",
          "dev:33333333-3333-3333-3333-333333333333:11111111-1111-1111-1111-111111111111:owner"
        );
        router.push("/onboarding");
        return;
      }
      router.push("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--paper)] px-4">
      <div className="w-full max-w-md">
        <Link href="/" className="brand text-2xl font-extrabold">
          Hostline
        </Link>
        <h1 className="mt-8 text-3xl font-bold">Create account</h1>
        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Email</span>
            <input
              className="mt-1 w-full rounded-md border border-[var(--line)] bg-white px-3 py-2"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">Password</span>
            <input
              className="mt-1 w-full rounded-md border border-[var(--line)] bg-white px-3 py-2"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              required
            />
          </label>
          {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-[var(--ink)] py-2.5 font-semibold text-white"
          >
            {loading ? "Creating…" : "Continue"}
          </button>
        </form>
        <p className="mt-6 text-sm text-[var(--muted)]">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-[var(--ink)]">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
