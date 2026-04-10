"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { createClient } from "@/lib/supabase/client";

export function UserChip() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? null);
    });
  }, []);

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
  }

  const displayEmail =
    email && email.length > 20 ? `${email.slice(0, 20)}...` : email;

  return (
    <div className="flex items-center gap-3">
      {/* Pulsing status dot */}
      <span className="relative flex h-2 w-2 items-center justify-center">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-green-400" />
      </span>

      {displayEmail && (
        <span
          className="text-[12.5px]"
          style={{ color: "rgba(255,255,255,0.8)" }}
        >
          {displayEmail}
        </span>
      )}

      <button
        onClick={handleSignOut}
        className="font-mono text-[11px] text-slate-400 transition-colors hover:text-white"
      >
        Sign out
      </button>
    </div>
  );
}
