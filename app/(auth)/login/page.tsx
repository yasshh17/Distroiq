"use client";

import { type FormEvent, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle2 } from "lucide-react";

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
      {/* DQ tile with glow */}
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

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

// useSearchParams requires Suspense — isolated into its own component.
function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resetSuccess = searchParams.get("reset") === "success";

  const [email, setEmail] = useState("");
  const [emailTouched, setEmailTouched] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const emailError =
    emailTouched && email.length > 0 && !isValidEmail(email)
      ? "Enter a valid email address."
      : null;

  const isFormValid = email.length > 0 && password.length > 0 && !emailError;

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!isFormValid) return;

    setIsLoading(true);
    setError(null);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setIsLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  }

  return (
    <div className="w-full max-w-[360px]">
      {/* Brand */}
      <div className="mb-8 flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
          <span className="font-mono text-[12px] font-bold text-white">DQ</span>
        </div>
        <span className="text-[17px] font-semibold text-slate-800">
          DistroIQ
        </span>
      </div>

      <h1 className="text-[24px] font-semibold tracking-tight text-slate-800">
        Sign in to your account
      </h1>
      <p className="mt-1.5 text-[13.5px] text-slate-400">
        Enter your credentials to continue
      </p>

      {/* Password-reset success banner */}
      {resetSuccess && (
        <div className="mt-5 flex items-start gap-2.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3.5 py-3">
          <CheckCircle2 className="mt-px h-4 w-4 shrink-0 text-emerald-600" />
          <p className="text-[12.5px] leading-snug text-emerald-700">
            Password updated. Please sign in with your new password.
          </p>
        </div>
      )}

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
            onBlur={() => setEmailTouched(true)}
            required
            autoComplete="email"
            className={
              emailError
                ? "border-red-400 focus-visible:ring-red-200"
                : undefined
            }
          />
          {emailError !== null && (
            <p className="text-[11.5px] text-red-500">{emailError}</p>
          )}
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor="password"
            className="block font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
          >
            Password
          </label>
          <Input
            id="password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
          <div className="flex justify-end">
            <Link
              href="/forgot-password"
              className="text-sm text-blue-600 hover:underline"
            >
              Forgot password?
            </Link>
          </div>
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
          disabled={isLoading || !isFormValid}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in…
            </>
          ) : (
            "Sign in"
          )}
        </Button>
      </form>

      <p className="mt-5 text-center text-[13px] text-slate-400">
        Don&apos;t have an account?{" "}
        <Link
          href="/signup"
          className="font-medium text-blue-600 hover:text-blue-700"
        >
          Sign up
        </Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="flex h-screen">
      {/* ── Left: form ─────────────────────────────────────────────── */}
      <div className="flex w-full flex-col items-center justify-center bg-white px-8 lg:w-[60%]">
        <Suspense fallback={null}>
          <LoginForm />
        </Suspense>
      </div>

      {/* ── Right: branding ────────────────────────────────────────── */}
      <RightPanel />
    </div>
  );
}
