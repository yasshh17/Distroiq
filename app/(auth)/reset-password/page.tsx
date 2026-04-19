"use client";

import { type FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { createClient } from "@/lib/supabase/client";

const BULLETS = [
  {
    title: "Real-time Network Monitoring",
    desc: "Sub-millisecond latency for global distribution telemetry tracking.",
  },
  {
    title: "Kinetic Load Balancing",
    desc: "Automated asset allocation driven by predictive algorithmic models.",
  },
  {
    title: "Hardware-level Encryption",
    desc: "End-to-end security protocols for critical infrastructure access.",
  },
];

function RightPanel() {
  return (
    <div className="hidden lg:flex lg:w-[45%] flex-col items-center justify-center bg-[#101c2e] px-14">
      <div
        className="relative flex h-[280px] w-[280px] items-center justify-center rounded-full"
        style={{ border: "1px solid rgba(37,99,235,0.1)" }}
      >
        <span
          className="font-grotesk font-bold select-none"
          style={{ fontSize: "96px", color: "rgba(37,99,235,0.2)", lineHeight: 1 }}
        >
          DQ
        </span>
      </div>

      <h2 className="mt-8 text-[24px] font-normal text-white/95" style={{ fontFamily: "'Inter', sans-serif" }}>
        Built for distribution operations
      </h2>

      <ul className="mt-7 w-full max-w-[300px] space-y-5">
        {BULLETS.map((b) => (
          <li key={b.title} className="flex items-start gap-3">
            <span className="mt-1.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-[#2563eb]/15 ring-1 ring-[#2563eb]/30">
              <span className="h-1.5 w-1.5 rounded-full bg-[#3b82f6]" />
            </span>
            <div>
              <p className="text-[13px] font-medium text-white/90">{b.title}</p>
              <p className="mt-0.5 text-[12px] leading-snug text-white/45">{b.desc}</p>
            </div>
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

  useEffect(() => {
    if (window.location.hash.includes("error_code")) {
      setLinkInvalid(true);
    }
  }, []);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (newPassword.length < 8) { setError("Password must be at least 8 characters."); return; }
    if (newPassword !== confirmPassword) { setError("Passwords do not match."); return; }

    setIsLoading(true);
    setError(null);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.updateUser({ password: newPassword });

    if (authError) {
      setError(authError.message);
      setIsLoading(false);
      return;
    }

    await supabase.auth.signOut();
    router.push("/login?reset=success");
  }

  const inputClass =
    "w-full rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] px-4 py-3 text-[14px] text-white/95 placeholder:text-white/25 outline-none transition-all focus:border-[#2563eb] focus:ring-4 focus:ring-[rgba(37,99,235,0.2)]";

  return (
    <div className="flex h-screen flex-col bg-[#071325]" style={{ backgroundImage: "radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)", backgroundSize: "24px 24px" }}>
      {/* Top nav bar */}
      <nav className="flex h-12 shrink-0 items-center justify-between border-b border-white/[0.08] px-6 sm:px-8">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#2563eb]">
            <span className="font-grotesk text-[9px] font-bold text-white">DQ</span>
          </div>
          <span className="font-grotesk text-[14px] font-bold text-white">DISTROIQ</span>
        </div>
        <span className="font-grotesk text-[11px] uppercase tracking-widest text-white/30">
          ● Secure Session · TLS 1.5
        </span>
      </nav>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel */}
        <div className="flex w-full flex-col items-start justify-center px-8 sm:px-12 lg:w-[55%] lg:px-16">
          <div className="w-full max-w-[400px]">
            {linkInvalid ? (
              <div>
                <p className="rounded-[12px] border border-[#ef4444]/25 bg-[#ef4444]/10 px-4 py-3 text-[13px] leading-relaxed text-[#ef4444]">
                  Reset link has expired or is invalid. Request a new one.
                </p>
                <Link
                  href="/forgot-password"
                  className="mt-5 block font-grotesk text-[11px] uppercase tracking-widest text-[#2563eb] hover:text-[#3b82f6] transition-colors"
                >
                  ← Request a new reset link
                </Link>
              </div>
            ) : (
              <>
                <h1 className="text-[36px] font-light text-white/95 tracking-tight" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Set new access key
                </h1>
                <p className="mt-2 text-[14px] text-white/55">
                  Choose a strong password for your account
                </p>

                <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                  <div className="space-y-2">
                    <label className="font-grotesk block text-[11px] uppercase tracking-widest text-white/30">
                      New Access Key{" "}
                      <span className="normal-case tracking-normal text-white/25">(min. 8 characters)</span>
                    </label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={8}
                      autoComplete="new-password"
                      className={inputClass}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="font-grotesk block text-[11px] uppercase tracking-widest text-white/30">
                      Confirm Access Key
                    </label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      autoComplete="new-password"
                      className={inputClass}
                    />
                  </div>

                  {error !== null && (
                    <p className="rounded-[12px] border border-[#ef4444]/25 bg-[#ef4444]/10 px-4 py-3 text-[12.5px] text-[#ef4444]">
                      {error}
                    </p>
                  )}

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="font-grotesk w-full rounded-[12px] bg-[#2563eb] py-3.5 text-[13px] font-semibold uppercase tracking-widest text-white transition-colors hover:bg-[#1d4ed8] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Updating…
                      </span>
                    ) : (
                      "Update Access Key"
                    )}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>

        {/* Right panel */}
        <RightPanel />
      </div>

      {/* Footer */}
      <footer className="shrink-0 border-t border-white/[0.08] px-6 py-3 sm:px-8">
        <p className="font-grotesk text-[10px] uppercase tracking-widest text-white/25">
          © 2026 DistroIQ Kinetic Precision · Privacy · Terms · Node: US-EAST-01
        </p>
      </footer>
    </div>
  );
}
