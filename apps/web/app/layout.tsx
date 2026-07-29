import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hostline — AI phone host for restaurants",
  description: "Answer every call, book tables, and answer menu questions with an ElevenLabs-powered voice agent.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
