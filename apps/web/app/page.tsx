import Link from "next/link";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[var(--ink)] text-white">
      <div
        className="pointer-events-none absolute inset-0 opacity-90"
        style={{
          background:
            "radial-gradient(ellipse 80% 60% at 70% 20%, rgba(200,241,53,0.22), transparent 55%), radial-gradient(ellipse 50% 40% at 10% 80%, rgba(88,140,255,0.18), transparent 50%), linear-gradient(160deg, #0c1222 0%, #141c2e 55%, #0a101c 100%)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        }}
      />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="brand text-2xl font-extrabold tracking-tight">Hostline</span>
        <nav className="flex items-center gap-4 text-sm text-white/80">
          <Link href="/login" className="hover:text-white">
            Sign in
          </Link>
          <Link
            href="/signup"
            className="rounded-md bg-[var(--accent)] px-4 py-2 font-semibold text-[var(--ink)] transition hover:bg-[var(--accent-deep)]"
          >
            Start free
          </Link>
        </nav>
      </header>

      <section className="relative z-10 mx-auto grid max-w-6xl gap-12 px-6 pb-24 pt-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:pt-24">
        <div>
          <h1 className="brand animate-rise text-5xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
            Hostline
          </h1>
          <p className="animate-rise-delay mt-5 max-w-xl text-lg text-white/75 sm:text-xl">
            Your restaurant&apos;s AI phone host — answers calls, books tables, and speaks with an ElevenLabs voice.
          </p>
          <div className="animate-rise-delay mt-8 flex flex-wrap gap-3">
            <Link
              href="/signup"
              className="rounded-md bg-[var(--accent)] px-6 py-3 text-base font-semibold text-[var(--ink)] transition hover:bg-[var(--accent-deep)]"
            >
              Get started
            </Link>
            <Link
              href="/login"
              className="rounded-md border border-white/25 px-6 py-3 text-base font-medium text-white/90 hover:border-white/50"
            >
              Sign in
            </Link>
          </div>
        </div>

        <div className="relative animate-rise-delay hidden min-h-[320px] lg:block">
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm" />
          <div className="absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-4">
            <div className="pulse-ring relative flex h-28 w-28 items-center justify-center rounded-full bg-[var(--accent)] text-[var(--ink)]">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
                <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2Z" />
              </svg>
            </div>
            <p className="text-sm text-white/60">Live ElevenLabs voice · Twilio Media Streams</p>
          </div>
        </div>
      </section>

      <section className="relative z-10 border-t border-white/10 bg-[var(--ink-soft)]/80 px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="brand text-3xl font-bold">One number. Every answer.</h2>
          <p className="mt-3 max-w-2xl text-white/65">
            Hostline connects Twilio, OpenAI tool-calling, and ElevenLabs TTS so guests get hours, menu facts, and
            reservations without holding for the host stand.
          </p>
          <ul className="mt-10 grid gap-8 sm:grid-cols-3">
            {[
              ["Never miss a reservation", "Books tables and texts confirmation codes automatically."],
              ["Your voice, your brand", "Pick an ElevenLabs voice_id per restaurant in Agent settings."],
              ["Know what happened", "Call transcripts, outcomes, and minute usage in one dashboard."],
            ].map(([title, body]) => (
              <li key={title}>
                <h3 className="font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm text-white/60">{body}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <footer className="relative z-10 border-t border-white/10 px-6 py-8 text-center text-sm text-white/40">
        © {new Date().getFullYear()} Hostline
      </footer>
    </main>
  );
}
