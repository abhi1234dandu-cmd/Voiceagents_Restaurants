"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createClient } from "@/lib/supabase/client";

const DEV_TOKEN =
  "dev:33333333-3333-3333-3333-333333333333:11111111-1111-1111-1111-111111111111:owner";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function enterDemo() {
    localStorage.setItem("hostline_dev_token", DEV_TOKEN);
    router.push("/app");
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const supabase = createClient();
      const { error: err } = await supabase.auth.signInWithPassword({ email, password });
      if (err) {
        if (email.includes("dev") || process.env.NODE_ENV === "development") {
          enterDemo();
          return;
        }
        throw err;
      }
      router.push("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed — use the demo button below for local mode.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="relative hidden overflow-hidden lg:block">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1600&q=80"
          alt=""
          className="hero-media h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[var(--espresso)] via-[var(--espresso)]/50 to-transparent" />
        <div className="absolute bottom-0 left-0 p-12">
          <p className="brand text-4xl font-bold text-[var(--linen)]">Hostline</p>
          <p className="mt-3 max-w-sm text-[var(--linen)]/70">
            Your dining room&apos;s voice on every missed call.
          </p>
        </div>
      </section>

      <section className="flex items-center justify-center bg-[var(--linen)] px-6 py-16">
        <div className="w-full max-w-md animate-rise">
          <Link href="/" className="brand text-2xl font-bold text-[var(--ink)] lg:hidden">
            Hostline
          </Link>
          <h1 className="mt-8 text-3xl font-bold text-[var(--ink)] sm:mt-0">Welcome back</h1>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Local mode works without Supabase — use the demo button.
          </p>

          <button type="button" onClick={enterDemo} className="btn-primary mt-8 w-full !bg-[var(--olive)] !text-white hover:!bg-[var(--olive-bright)]">
            Enter demo dashboard
          </button>

          <div className="my-8 flex items-center gap-3 text-xs uppercase tracking-wider text-[var(--muted)]">
            <span className="h-px flex-1 bg-[var(--line)]" />
            or sign in
            <span className="h-px flex-1 bg-[var(--line)]" />
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <label className="block text-sm">
              <span className="text-[var(--muted)]">Email</span>
              <input
                className="field"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@restaurant.com"
                required
              />
            </label>
            <label className="block text-sm">
              <span className="text-[var(--muted)]">Password</span>
              <input
                className="field"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </label>
            {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="mt-6 text-sm text-[var(--muted)]">
            New here?{" "}
            <Link href="/signup" className="font-semibold text-[var(--ink)] underline">
              Create an account
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
