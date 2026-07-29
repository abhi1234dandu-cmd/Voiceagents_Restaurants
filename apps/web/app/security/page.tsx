import Link from "next/link";

export default function SecurityPage() {
  return (
    <main className="min-h-screen bg-[var(--linen)] text-[var(--ink)]">
      <header className="border-b border-[var(--line)] bg-[var(--espresso)] text-[var(--linen)]">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-6">
          <Link href="/" className="brand text-2xl font-bold">Hostline</Link>
          <Link href="/login" className="btn-primary !py-2.5">Open demo</Link>
        </div>
      </header>
      <article className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--olive)]">Trust</p>
        <h1 className="brand mt-3 text-4xl font-bold">Security</h1>
        <p className="mt-4 text-[var(--muted)]">
          Hostline is built multi-tenant from day one. Restaurant data is scoped by organization; voice recordings and
          transcripts stay with the location that received the call.
        </p>
        <ul className="mt-10 space-y-6 text-sm leading-relaxed text-[var(--ink)]">
          <li>
            <strong>Tenant isolation</strong>
            <p className="mt-1 text-[var(--muted)]">PostgreSQL RLS and server-side org checks on every dashboard API.</p>
          </li>
          <li>
            <strong>Webhook authenticity</strong>
            <p className="mt-1 text-[var(--muted)]">Twilio and Stripe signatures verified before mutating call or billing state.</p>
          </li>
          <li>
            <strong>Secrets</strong>
            <p className="mt-1 text-[var(--muted)]">API keys live in environment config — never in the browser bundle except public publishable keys.</p>
          </li>
          <li>
            <strong>Recordings</strong>
            <p className="mt-1 text-[var(--muted)]">Stored with retention controls; access via signed URLs in production.</p>
          </li>
        </ul>
        <Link href="/pricing" className="mt-12 inline-block text-sm font-semibold text-[var(--olive)] underline">
          View pricing →
        </Link>
      </article>
    </main>
  );
}
