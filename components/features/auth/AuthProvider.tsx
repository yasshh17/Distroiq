"use client";

import { useEffect } from "react";

import { useAuthStore } from "@/stores/auth";
import { startKeepAlive } from "@/lib/api";

// ── Full-screen loader shown while auth state is resolving ────────────

function AuthLoadingScreen() {
  return (
    <div className="flex h-screen items-center justify-center bg-[#0f1623]">
      <div className="relative flex h-16 w-16 items-center justify-center">
        {/* Spinning ring */}
        <div className="absolute inset-0 animate-spin rounded-2xl border-2 border-white/5 border-t-blue-500" />
        {/* DQ tile */}
        <div
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600"
          style={{ boxShadow: "0 0 0 4px rgba(37,99,235,0.15)" }}
        >
          <span className="font-mono text-[14px] font-bold text-white">DQ</span>
        </div>
      </div>
    </div>
  );
}

// ── Provider ─────────────────────────────────────────────────────────

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const initialize = useAuthStore((s) => s.initialize);
  const isLoading = useAuthStore((s) => s.isLoading);

  useEffect(() => {
    initialize();
    startKeepAlive();
    // initialize is a stable store function — safe to omit from deps,
    // but included to satisfy exhaustive-deps without a lint override.
  }, [initialize]);

  if (isLoading) {
    return <AuthLoadingScreen />;
  }

  return <>{children}</>;
}
