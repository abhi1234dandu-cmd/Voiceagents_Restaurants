import Link from "next/link";

const TIERS = [
  {
    name: "Starter",
    price: "$249",
    period: "/month",
    blurb: "One location ready for every ring.",
    features: [
      "24/7 AI phone answering",
      "Answer menu questions",
      "Restaurant hours & directions",
      "Reservation booking",
      "Basic call analytics",
      "Email support",
      "Up to 500 AI minutes",
    ],
    cta: "Start with Starter",
    featured: false,
  },
  {
    name: "Professional",
    price: "$499",
    period: "/month",
    blurb: "Everything in Starter, plus guest follow-through.",
    features: [
      "Everything in Starter",
      "SMS reservation confirmation",
      "Multilingual support",
      "Catering inquiry handling",
      "Advanced analytics dashboard",
      "Priority support",
      "Up to 2,000 AI minutes",
    ],
    cta: "Choose Professional",
    featured: true,
  },
  {
    name: "Premium",
    price: "From $999",
    period: "/month",
    blurb: "Built for busy single sites and growing groups.",
    features: [
      "Everything in Professional",
      "Multiple restaurant locations",
      "POS integration",
      "Custom AI workflows",
      "Dedicated account manager",
      "Custom integrations",
      "Unlimited / custom usage",
    ],
    cta: "Talk about Premium",
    featured: false,
  },
];

const MULTI = [
  { label: "1 location", price: "$999/month" },
  { label: "2–5 locations", price: "$2,500–$4,000/month" },
  { label: "6–20 locations", price: "$5,000–$10,000/month" },
  { label: "20+ locations", price: "Custom enterprise" },
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-[var(--linen)] text-[var(--ink)]">
      <header className="border-b border-[var(--line)] bg-[var(--espresso)] text-[var(--linen)]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <Link href="/" className="brand text-2xl font-bold">
            Hostline
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/login" className="text-[var(--linen)]/75 hover:text-[var(--linen)]">
              Sign in
            </Link>
            <Link href="/login" className="btn-primary !py-2.5 !px-4">
              Open demo
            </Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 pb-10 pt-16">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--olive)]">Pricing</p>
        <h1 className="brand mt-3 max-w-2xl text-4xl font-bold leading-tight sm:text-5xl">
          Plans for one dining room — or the whole chain.
        </h1>
        <p className="mt-4 max-w-xl text-[var(--muted)]">
          Starter and Professional cover a single location. Premium and Enterprise scale with your footprint.
        </p>
      </section>

      <section className="mx-auto grid max-w-6xl gap-6 px-6 pb-20 lg:grid-cols-3">
        {TIERS.map((tier) => (
          <div
            key={tier.name}
            className={`flex flex-col border p-7 ${
              tier.featured
                ? "border-[var(--espresso)] bg-[var(--espresso)] text-[var(--linen)]"
                : "border-[var(--line)] bg-white"
            }`}
          >
            <p
              className={`text-xs font-semibold uppercase tracking-[0.2em] ${
                tier.featured ? "text-[var(--brass)]" : "text-[var(--olive)]"
              }`}
            >
              {tier.name}
            </p>
            <p className="brand mt-4 text-4xl font-bold">
              {tier.price}
              <span className={`text-base font-sans font-medium ${tier.featured ? "text-[var(--linen)]/60" : "text-[var(--muted)]"}`}>
                {tier.period}
              </span>
            </p>
            <p className={`mt-3 text-sm ${tier.featured ? "text-[var(--linen)]/70" : "text-[var(--muted)]"}`}>
              {tier.blurb}
            </p>
            <ul className="mt-8 flex-1 space-y-3 text-sm">
              {tier.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span className={tier.featured ? "text-[var(--brass)]" : "text-[var(--olive)]"}>✓</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <Link
              href="/login"
              className={`mt-8 inline-flex justify-center rounded-sm px-5 py-3 text-sm font-semibold ${
                tier.featured
                  ? "bg-[var(--brass)] text-[var(--espresso)] hover:bg-[var(--brass-deep)]"
                  : "bg-[var(--espresso)] text-[var(--linen)] hover:bg-[var(--espresso-soft)]"
              }`}
            >
              {tier.cta}
            </Link>
          </div>
        ))}
      </section>

      <section className="border-t border-[var(--line)] bg-[var(--linen-deep)]/60 px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="brand text-3xl font-bold">Enterprise & multi-location</h2>
          <p className="mt-3 max-w-2xl text-[var(--muted)]">
            Starting at <strong className="text-[var(--ink)]">$2,500/month</strong> or a custom quote — priced by how many
            host stands you need on the line.
          </p>
          <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {MULTI.map((row) => (
              <div key={row.label} className="border border-[var(--line)] bg-white px-5 py-6">
                <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">{row.label}</p>
                <p className="brand mt-3 text-2xl font-bold">{row.price}</p>
              </div>
            ))}
          </div>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/login" className="btn-primary !bg-[var(--olive)] !text-white hover:!bg-[var(--olive-bright)]">
              Request enterprise quote
            </Link>
            <Link href="/" className="rounded-sm border border-[var(--line)] px-5 py-3 text-sm font-semibold">
              Back to Hostline
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-[var(--line)] px-6 py-8 text-center text-sm text-[var(--muted)]">
        © {new Date().getFullYear()} Hostline
      </footer>
    </main>
  );
}
