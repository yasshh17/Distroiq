"use client";

import { type FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

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

export default function ResetPasswordPage() {
  const router = useRouter();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [linkInvalid, setLinkInvalid] = useState(false);

  // Supabase appends error info to the URL hash when a reset link is
  // expired or already used: #error=access_denied&error_code=otp_expired&…
  useEffect(() => {
    const hash = window.location.hash;
    if (hash.includes("error_code")) {
      setLinkInvalid(true);
    }
  }, []);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (authError) {
      setError(authError.message);
      setIsLoading(false);
      return;
    }

    await supabase.auth.signOut();
    router.push("/login?reset=success");
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

          {linkInvalid ? (
            /* ── Expired / invalid link state ─────────────────────── */
            <div className="py-4">
              <p className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-3 text-[13px] leading-relaxed text-red-600">
                Reset link has expired or is invalid. Request a new one.
              </p>
              <p className="mt-5 text-center text-[13px] text-slate-400">
                <Link
                  href="/forgot-password"
                  className="font-medium text-blue-600 hover:text-blue-700"
                >
                  Request a new reset link
                </Link>
              </p>
            </div>
          ) : (
            /* ── Form ──────────────────────────────────────────────── */
            <>
              <h1 className="text-[24px] font-semibold tracking-tight text-slate-800">
                Set a new password
              </h1>
              <p className="mt-1.5 text-[13.5px] text-slate-400">
                Choose a strong password for your account
              </p>

              <form onSubmit={handleSubmit} className="mt-7 space-y-4">
                <div className="space-y-1.5">
                  <label
                    htmlFor="new_password"
                    className="block font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
                  >
                    New password
                    <span className="ml-1.5 font-mono text-[10px] normal-case tracking-normal text-slate-400">
                      (min. 8 characters)
                    </span>
                  </label>
                  <Input
                    id="new_password"
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                </div>

                <div className="space-y-1.5">
                  <label
                    htmlFor="confirm_password"
                    className="block font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
                  >
                    Confirm password
                  </label>
                  <Input
                    id="confirm_password"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
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
                      Updating…
                    </>
                  ) : (
                    "Update password"
                  )}
                </Button>
              </form>
            </>
          )}
        </div>
      </div>

      {/* ── Right: branding ────────────────────────────────────────── */}
      <RightPanel />
    </div>
  );
}
