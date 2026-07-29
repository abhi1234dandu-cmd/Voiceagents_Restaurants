"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { FAQ } from "@restaurant-voice/shared-types";

export default function FaqsPage() {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  function load() {
    apiFetch<FAQ[]>(`/v1/restaurants/${restaurantId}/faqs`).then(setFaqs);
  }
  useEffect(() => {
    load();
  }, [restaurantId]);

  async function add(e: FormEvent) {
    e.preventDefault();
    await apiFetch(`/v1/restaurants/${restaurantId}/faqs`, {
      method: "POST",
      body: JSON.stringify({ question, answer }),
    });
    setQuestion("");
    setAnswer("");
    load();
  }

  async function remove(id: string) {
    await apiFetch(`/v1/restaurants/${restaurantId}/faqs/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div>
      <h1 className="text-3xl font-bold">FAQs</h1>
      <form onSubmit={add} className="mt-6 space-y-3">
        <input className="w-full rounded-md border border-[var(--line)] px-3 py-2" placeholder="Question" value={question} onChange={(e) => setQuestion(e.target.value)} required />
        <textarea className="w-full rounded-md border border-[var(--line)] px-3 py-2" placeholder="Answer" rows={3} value={answer} onChange={(e) => setAnswer(e.target.value)} required />
        <button className="rounded-md bg-[var(--ink)] px-4 py-2 text-white">Add FAQ</button>
      </form>
      <ul className="mt-8 space-y-3">
        {faqs.map((f) => (
          <li key={f.id} className="rounded-lg border border-[var(--line)] bg-white p-4">
            <div className="flex justify-between gap-4">
              <div>
                <p className="font-medium">{f.question}</p>
                <p className="mt-1 text-sm text-[var(--muted)]">{f.answer}</p>
              </div>
              <button type="button" onClick={() => remove(f.id)} className="text-sm text-[var(--danger)]">
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
