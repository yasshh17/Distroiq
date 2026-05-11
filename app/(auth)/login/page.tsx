"use client";

import { type FormEvent, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, CheckCircle2 } from "lucide-react";
import {
  LazyMotion,
  domAnimation,
  m,
  AnimatePresence,
  MotionConfig,
} from "framer-motion";

import { createClient } from "@/lib/supabase/client";
import { DotPattern } from "@/components/ui/dot-pattern";
import { Spotlight } from "@/components/ui/spotlight-new";
import { BorderBeam } from "@/components/ui/border-beam";
import {
  navVariant,
  footerVariant,
  leftContainer,
  rightPanel,
  rightContainer,
  itemUp,
  itemLeft,
  watermarkVariant,
  DUR_MICRO,
  DUR_SHORT,
  EASE_STANDARD,
  EASE_OUT_EXPO,
  DIST_SM,
  DIST_MD,
} from "@/lib/motion";

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
    <m.div
      className="hidden lg:flex lg:w-[45%] flex-col items-center justify-center bg-[#101c2e] px-14"
      variants={rightPanel}
      initial="hidden"
      animate="visible"
    >
      <m.div variants={rightContainer} initial="hidden" animate="visible">
        {/* Watermark circle */}
        <m.div
          className="relative flex h-[280px] w-[280px] items-center justify-center rounded-full"
          style={{ border: "1px solid rgba(37,99,235,0.25)" }}
          variants={watermarkVariant}
        >
          <BorderBeam
            size={140}
            duration={12}
            colorFrom="#2563eb"
            colorTo="rgba(59,130,246,0)"
            borderWidth={1}
          />
          <span
            className="font-grotesk font-bold select-none"
            style={{ fontSize: "96px", color: "rgba(37,99,235,0.2)", lineHeight: 1 }}
          >
            DQ
          </span>
        </m.div>

        <m.h2
          variants={itemUp}
          className="mt-8 text-[24px] font-normal text-white/95"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Built for distribution operations
        </m.h2>

        <m.ul className="mt-7 w-full max-w-[300px] space-y-5" variants={rightContainer}>
          {BULLETS.map((b) => (
            <m.li key={b.title} variants={itemLeft} className="flex items-start gap-3">
              <span className="mt-1.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-[#2563eb]/15 ring-1 ring-[#2563eb]/30">
                <span className="h-1.5 w-1.5 rounded-full bg-[#3b82f6]" />
              </span>
              <div>
                <p className="text-[13px] font-medium text-white/90">{b.title}</p>
                <p className="mt-0.5 text-[12px] leading-snug text-white/45">{b.desc}</p>
              </div>
            </m.li>
          ))}
        </m.ul>
      </m.div>
    </m.div>
  );
}

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const resetSuccess = searchParams.get("reset") === "success";

  const [email, setEmail] = useState("");
  const [emailTouched, setEmailTouched] = useState(false);
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const emailError =
    emailTouched && email.length > 0 && !isValidEmail(email)
      ? "Enter a valid email address."
      : null;

  const isFormValid = email.length > 0 && password.length > 0 && !emailError;
  const isDisabled = isLoading || !isFormValid;

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!isFormValid) return;

    setIsLoading(true);
    setError(null);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password });

    if (authError) {
      setError(authError.message);
      setIsLoading(false);
      return;
    }

    router.push("/");
    router.refresh();
  }

  return (
    <m.div
      className="w-full max-w-[400px]"
      variants={leftContainer}
      initial="hidden"
      animate="visible"
    >
      <m.h1
        variants={itemUp}
        className="text-[36px] font-light text-white/95 tracking-tight"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        Sign in to your account
      </m.h1>
      <m.p variants={itemUp} className="mt-2 text-[14px] text-white/55">
        Operational access for authorized personnel only
      </m.p>

      <AnimatePresence initial={false}>
        {resetSuccess && (
          <m.div
            key="reset-banner"
            initial={{ opacity: 0, y: -DIST_SM }}
            animate={{ opacity: 1, y: 0, transition: { duration: DUR_SHORT, ease: EASE_OUT_EXPO } }}
            exit={{ opacity: 0 }}
            className="mt-6 flex items-start gap-2.5 rounded-[12px] border border-[#22c55e]/25 bg-[#22c55e]/10 px-4 py-3"
          >
            <CheckCircle2 className="mt-px h-4 w-4 shrink-0 text-[#22c55e]" />
            <p className="text-[12.5px] leading-snug text-[#22c55e]">
              Password updated. Please sign in with your new password.
            </p>
          </m.div>
        )}
      </AnimatePresence>

      <m.form variants={itemUp} onSubmit={handleSubmit} className="mt-8 space-y-5">
        {/* Email */}
        <m.div variants={itemUp} className="space-y-2">
          <label className="font-grotesk block text-[11px] uppercase tracking-widest text-white/30">
            Command Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => setEmailTouched(true)}
            placeholder="user@enterprise.com"
            required
            autoComplete="email"
            aria-invalid={emailError !== null}
            aria-describedby={emailError !== null ? "email-error" : undefined}
            className="w-full rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] px-4 py-3 text-[14px] text-white/95 placeholder:text-white/25 outline-none transition-all focus:border-[#2563eb] focus:ring-4 focus:ring-[rgba(37,99,235,0.2)]"
          />
          <div className="min-h-[16px]">
            <AnimatePresence initial={false}>
              {emailError !== null && (
                <m.p
                  id="email-error"
                  key="email-error"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1, transition: { duration: DUR_SHORT } }}
                  exit={{ opacity: 0 }}
                  className="font-grotesk text-[11px] text-[#ef4444]"
                >
                  {emailError}
                </m.p>
              )}
            </AnimatePresence>
          </div>
        </m.div>

        {/* Password */}
        <m.div variants={itemUp} className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="font-grotesk block text-[11px] uppercase tracking-widest text-white/30">
              Access Key
            </label>
            <Link
              href="/forgot-password"
              className="font-grotesk text-[11px] uppercase tracking-widest text-[#2563eb] hover:text-[#3b82f6] transition-colors"
            >
              Forgot Password?
            </Link>
          </div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            autoComplete="current-password"
            className="w-full rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] px-4 py-3 text-[14px] text-white/95 placeholder:text-white/25 outline-none transition-all focus:border-[#2563eb] focus:ring-4 focus:ring-[rgba(37,99,235,0.2)]"
          />
        </m.div>

        {/* Remember session */}
        <m.label variants={itemUp} className="flex cursor-pointer items-center gap-2.5">
          <input
            type="checkbox"
            checked={remember}
            onChange={(e) => setRemember(e.target.checked)}
            className="h-3.5 w-3.5 rounded border-white/20 bg-[#1f2a3d] accent-[#2563eb]"
          />
          <span className="font-grotesk text-[11px] uppercase tracking-widest text-white/30">
            Remember Terminal Session
          </span>
        </m.label>

        <AnimatePresence initial={false}>
          {error !== null && (
            <m.p
              key="auth-error"
              initial={{ opacity: 0, y: DIST_MD }}
              animate={{ opacity: 1, y: 0, transition: { duration: DUR_SHORT, ease: EASE_OUT_EXPO } }}
              exit={{ opacity: 0, y: -2 }}
              className="rounded-[12px] border border-[#ef4444]/25 bg-[#ef4444]/10 px-4 py-3 text-[12.5px] text-[#ef4444]"
            >
              {error}
            </m.p>
          )}
        </AnimatePresence>

        <m.div variants={itemUp}>
          <m.button
            type="submit"
            disabled={isDisabled}
            whileHover={!isDisabled ? { scale: 1.01 } : undefined}
            whileTap={!isDisabled ? { scale: 0.99 } : undefined}
            transition={{ duration: DUR_MICRO, ease: EASE_STANDARD }}
            className="font-grotesk w-full rounded-[12px] bg-[#2563eb] py-3.5 text-[13px] font-semibold uppercase tracking-widest text-white transition-colors hover:bg-[#1d4ed8] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Signing in…
              </span>
            ) : (
              "Sign In"
            )}
          </m.button>
        </m.div>
      </m.form>

      <m.div variants={itemUp} className="my-6 border-t border-white/[0.08]" />

      <m.p variants={itemUp} className="text-center text-[13px] text-white/45">
        Don&apos;t have an account?{" "}
        <Link
          href="/signup"
          className="font-medium text-[#2563eb] hover:text-[#3b82f6] transition-colors"
        >
          Request Access
        </Link>
      </m.p>
    </m.div>
  );
}

export default function LoginPage() {
  return (
    <LazyMotion features={domAnimation}>
      <MotionConfig reducedMotion="user">
        <div className="relative flex h-screen flex-col bg-[#071325] overflow-hidden">
          {/* Background layers — present at first paint, never animate */}
          <DotPattern
            width={24}
            height={24}
            cx={1}
            cy={1}
            cr={1}
            className="text-white/[0.03] [mask-image:radial-gradient(800px_circle_at_30%_50%,white,transparent)]"
          />
          <Spotlight />

          {/* Top nav bar */}
          <m.nav
            variants={navVariant}
            initial="hidden"
            animate="visible"
            className="relative z-10 flex h-12 shrink-0 items-center justify-between border-b border-white/[0.08] px-6 sm:px-8"
          >
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-[#2563eb]">
                <span className="font-grotesk text-[9px] font-bold text-white">DQ</span>
              </div>
              <span className="font-grotesk text-[14px] font-bold text-white">DISTROIQ</span>
            </div>
            <span className="font-grotesk text-[11px] uppercase tracking-widest text-white/30">
              ● Secure Session · TLS 1.5
            </span>
          </m.nav>

          {/* Main content */}
          <div className="relative z-10 flex flex-1 overflow-hidden">
            {/* Left panel */}
            <div className="flex w-full flex-col items-start justify-center px-8 sm:px-12 lg:w-[55%] lg:px-16">
              <Suspense fallback={null}>
                <LoginForm />
              </Suspense>
            </div>

            {/* Right panel */}
            <RightPanel />
          </div>

          {/* Footer */}
          <m.footer
            variants={footerVariant}
            initial="hidden"
            animate="visible"
            className="relative z-10 shrink-0 border-t border-white/[0.08] px-6 py-3 sm:px-8"
          >
            <p className="font-grotesk text-[10px] uppercase tracking-widest text-white/25">
              © 2026 DistroIQ Kinetic Precision · Privacy · Terms · Node: US-EAST-01
            </p>
          </m.footer>
        </div>
      </MotionConfig>
    </LazyMotion>
  );
}
