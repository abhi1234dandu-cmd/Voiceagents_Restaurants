"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createClient } from "@/lib/supabase/client";

const DEV_TOKEN =
  "dev:33333333-3333-3333-3333-333333333333:11111111-1111-1111-1111-111111111111:owner";

export default function SignupPage() {
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
      const { error: err } = await supabase.auth.signUp({ email, password });
      if (err) {
        localStorage.setItem("hostline_dev_token", DEV_TOKEN);
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
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="relative hidden overflow-hidden lg:block">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1600&q=80"
          alt=""
          className="hero-media h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[var(--espresso)] via-[var(--espresso)]/40 to-transparent" />
        <div className="absolute bottom-0 p-12">
          <p className="brand text-4xl font-bold text-[var(--linen)]">Hostline</p>
          <p className="mt-3 max-w-sm text-[var(--linen)]/70">Open every night. Answer every ring.</p>
        </div>
      </section>
      <section className="flex items-center justify-center bg-[var(--linen)] px-6 py-16">
        <div className="w-full max-w-md animate-rise">
          <Link href="/" className="brand text-2xl font-bold text-[var(--ink)]">
            Hostline
          </Link>
          <h1 className="mt-8 text-3xl font-bold">Create your account</h1>
          <p className="mt-2 text-sm text-[var(--muted)]">Or jump straight into the demo dining room.</p>
          <button
            type="button"
            onClick={enterDemo}
            className="btn-primary mt-8 w-full !bg-[var(--olive)] !text-white hover:!bg-[var(--olive-bright)]"
          >
            Enter demo dashboard
          </button>
          <div className="my-8 flex items-center gap-3 text-xs uppercase tracking-wider text-[var(--muted)]">
            <span className="h-px flex-1 bg-[var(--line)]" />
            or sign up
            <span className="h-px flex-1 bg-[var(--line)]" />
          </div>
          <form onSubmit={onSubmit} className="space-y-4">
            <label className="block text-sm">
              <span className="text-[var(--muted)]">Email</span>
              <input className="field" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </label>
            <label className="block text-sm">
              <span className="text-[var(--muted)]">Password</span>
              <input
                className="field"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={6}
                required
              />
            </label>
            {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Creating…" : "Create account"}
            </button>
          </form>
          <p className="mt-6 text-sm text-[var(--muted)]">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-[var(--ink)] underline">
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
