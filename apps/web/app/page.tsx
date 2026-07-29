import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--espresso)] text-[var(--linen)]">
      {/* Full-bleed hero — one composition */}
      <section className="relative min-h-[100svh] overflow-hidden">
        <div className="absolute inset-0">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=2400&q=80"
            alt=""
            className="hero-media h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[var(--espresso)] via-[var(--espresso)]/85 to-[var(--espresso)]/35" />
          <div className="absolute inset-0 bg-gradient-to-t from-[var(--espresso)] via-transparent to-[var(--espresso)]/40" />
        </div>

        <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-7">
          <span className="brand text-2xl font-bold tracking-tight text-[var(--linen)] sm:text-3xl">
            Hostline
          </span>
          <nav className="flex items-center gap-5 text-sm text-[var(--linen)]/80">
            <Link href="/login" className="hidden hover:text-[var(--linen)] sm:inline">
              Sign in
            </Link>
            <Link href="/login" className="btn-primary !py-2.5 !px-4">
              Open demo
            </Link>
          </nav>
        </header>

        <div className="relative z-10 mx-auto flex max-w-6xl flex-col justify-end px-6 pb-20 pt-24 sm:pb-28 sm:pt-36">
          <p className="animate-rise glow-line mb-5 max-w-xs text-xs font-semibold uppercase tracking-[0.28em] text-[var(--brass)]">
            AI phone host for restaurants
          </p>
          <h1 className="brand animate-rise max-w-3xl text-5xl font-bold leading-[1.02] tracking-tight text-[var(--linen)] sm:text-6xl lg:text-7xl">
            Hostline
          </h1>
          <p className="animate-rise-delay mt-6 max-w-lg text-lg leading-relaxed text-[var(--linen)]/75 sm:text-xl">
            Answers every call, books the table, and speaks in your restaurant&apos;s voice — powered by ElevenLabs.
          </p>
          <div className="animate-rise-late mt-10 flex flex-wrap gap-3">
            <Link href="/login" className="btn-primary">
              Try the live demo
            </Link>
            <Link href="/signup" className="btn-ghost">
              Create account
            </Link>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-[var(--espresso-soft)] px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <h2 className="brand max-w-xl text-3xl font-bold text-[var(--linen)] sm:text-4xl">
            The host stand that never puts guests on hold.
          </h2>
          <p className="mt-4 max-w-2xl text-[var(--linen)]/65">
            Twilio brings the call in. OpenAI decides. ElevenLabs speaks. Your dashboard keeps the transcript.
          </p>
          <div className="mt-14 grid gap-12 sm:grid-cols-3">
            {[
              ["Reservations", "Confirms party size and time, then texts a confirmation code."],
              ["Menu & hours", "Answers from your FAQ and menu — no hold music, no missed rings."],
              ["Human handoff", "Warm-transfers to your floor when a guest asks for a person."],
            ].map(([title, body]) => (
              <div key={title}>
                <h3 className="font-semibold text-[var(--brass)]">{title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[var(--linen)]/65">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-white/10 px-6 py-10 text-center text-sm text-[var(--linen)]/40">
        © {new Date().getFullYear()} Hostline · Built for the dining room
      </footer>
    </main>
  );
}
