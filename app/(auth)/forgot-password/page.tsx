"use client";

import { type FormEvent, useState } from "react";
import Link from "next/link";
import { Loader2, MailCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createClient } from "@/lib/supabase/client";

const BULLETS = [
  "RAG-powered answers from live operational data",
  "Inventory, orders, customers — all in one place",
  "Streaming AI responses in real time",
];

function RightPanel() {
  return (
    <div className="hidden flex-col items-center justify-center bg-[#0f1623] px-14 lg:flex lg:w-[40%]">
      <div
        className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-600"
        style={{
          boxShadow:
            "0 0 0 8px rgba(37,99,235,0.12), 0 10px 36px rgba(37,99,235,0.35)",
        }}
      >
        <span className="font-mono text-[17px] font-bold text-white">DQ</span>
      </div>

      <h2 className="mt-8 text-[21px] font-semibold tracking-tight text-white">
        Built for distribution operations
      </h2>

      <ul className="mt-7 w-full max-w-[280px] space-y-4">
        {BULLETS.map((point) => (
          <li key={point} className="flex items-start gap-3">
            <span className="mt-[3px] flex h-[18px] w-[18px] shrink-0 items-center justify-center rounded-full bg-blue-500/15 ring-1 ring-blue-500/30">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
            </span>
            <span className="text-[13.5px] leading-snug text-slate-300">
              {point}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const supabase = createClient();
      const { error: authError } = await supabase.auth.resetPasswordForEmail(
        email,
        { redirectTo: `${window.location.origin}/reset-password` },
      );

      // Only surface genuine technical/network failures.
      // Never reveal whether the email address exists in the system.
      if (authError && authError.status !== 400) {
        setError("Something went wrong. Please try again.");
        setIsLoading(false);
        return;
      }
    } catch {
      setError("Something went wrong. Please try again.");
      setIsLoading(false);
      return;
    }

    // Always show success regardless of whether the account exists.
    setSubmitted(true);
  }

  return (
    <div className="flex h-screen">
      {/* ── Left: form ─────────────────────────────────────────────── */}
      <div className="flex w-full flex-col items-center justify-center bg-white px-8 lg:w-[60%]">
        <div className="w-full max-w-[360px]">
          {/* Brand */}
          <div className="mb-8 flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
              <span className="font-mono text-[12px] font-bold text-white">
                DQ
              </span>
            </div>
            <span className="text-[17px] font-semibold text-slate-800">
              DistroIQ
            </span>
          </div>

          {submitted ? (
            /* ── Success state ─────────────────────────────────────── */
            <div className="flex flex-col items-center py-6 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100">
                <MailCheck className="h-7 w-7 text-emerald-600" />
              </div>
              <h2 className="mt-5 text-[22px] font-semibold tracking-tight text-slate-800">
                Check your email
              </h2>
              <p className="mt-2 max-w-[280px] text-[13.5px] leading-relaxed text-slate-400">
                If an account exists for this email, you&apos;ll receive a reset
                link shortly.
              </p>
              <p className="mt-6 text-[13px] text-slate-400">
                <Link
                  href="/login"
                  className="font-medium text-blue-600 hover:text-blue-700"
                >
                  Back to sign in
                </Link>
              </p>
            </div>
          ) : (
            /* ── Form ──────────────────────────────────────────────── */
            <>
              <h1 className="text-[24px] font-semibold tracking-tight text-slate-800">
                Reset your password
              </h1>
              <p className="mt-1.5 text-[13.5px] text-slate-400">
                Enter your email and we&apos;ll send you a reset link
              </p>

              <form onSubmit={handleSubmit} className="mt-7 space-y-4">
                <div className="space-y-1.5">
                  <label
                    htmlFor="email"
                    className="block font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
                  >
                    Email
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                  />
                </div>

                {error !== null && (
                  <p className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-[12.5px] text-red-600">
                    {error}
                  </p>
                )}

                <Button
                  type="submit"
                  size="lg"
                  className="w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Sending…
                    </>
                  ) : (
                    "Send reset link"
                  )}
                </Button>
              </form>

              <p className="mt-5 text-center text-[13px] text-slate-400">
                <Link
                  href="/login"
                  className="font-medium text-blue-600 hover:text-blue-700"
                >
                  Back to sign in
                </Link>
              </p>
            </>
          )}
        </div>
      </div>

      {/* ── Right: branding ────────────────────────────────────────── */}
      <RightPanel />
    </div>
  );
}
