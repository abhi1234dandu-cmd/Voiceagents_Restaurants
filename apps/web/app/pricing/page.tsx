import Link from "next/link";

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-[var(--espresso)] text-[var(--linen)]">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-7">
        <Link href="/" className="brand text-2xl font-bold">Hostline</Link>
        <Link href="/login" className="btn-primary !py-2.5">Open demo</Link>
      </header>
      <section className="mx-auto max-w-5xl px-6 py-16">
        <h1 className="brand text-5xl font-bold">Simple pricing for busy floors</h1>
        <p className="mt-4 max-w-xl text-[var(--linen)]/70">Start on demo. Upgrade when you put a real Twilio number on the host stand.</p>
        <div className="mt-14 grid gap-6 sm:grid-cols-2">
          {[
            ["Demo", "Free", "Local in-memory agent, sample menu & calls", "Enter demo"],
            ["Pro", "$99/mo", "Live number, ElevenLabs voice, transcripts, SMS confirmations", "Start free"],
          ].map(([name, price, body, cta]) => (
            <div key={name} className="border border-white/15 bg-[var(--espresso-soft)] p-8">
              <p className="text-xs uppercase tracking-[0.22em] text-[var(--brass)]">{name}</p>
              <p className="brand mt-3 text-4xl font-bold">{price}</p>
              <p className="mt-4 text-sm text-[var(--linen)]/65">{body}</p>
              <Link href="/login" className="btn-primary mt-8 inline-flex">{cta}</Link>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
