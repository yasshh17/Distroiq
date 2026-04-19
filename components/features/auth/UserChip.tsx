"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronUp, LogOut, Trash2 } from "lucide-react";

import { DeleteAccountModal } from "@/components/features/auth/DeleteAccountModal";
import { createClient } from "@/lib/supabase/client";

export function UserChip() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? null);
    });
  }, []);

  // Close on outside click
  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  async function handleSignOut() {
    setOpen(false);
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
  }

  const displayEmail =
    email && email.length > 22 ? `${email.slice(0, 22)}…` : email;

  return (
    <>
      <div ref={ref} className="relative flex items-center gap-2">
        {displayEmail && (
          <span className="hidden text-[12px] text-white/50 sm:block">
            {displayEmail}
          </span>
        )}

        {/* Trigger */}
        <button
          onClick={() => setOpen((o) => !o)}
          className="font-grotesk flex items-center gap-1.5 rounded-lg px-2 py-1 text-[12px] uppercase tracking-wide text-white/55 transition-colors hover:text-white/95"
        >
          Account
          {open ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
        </button>

        {/* Custom dropdown */}
        {open && (
          <div
            className="absolute right-0 top-full z-50 mt-2 min-w-[220px] rounded-[12px] border border-white/[0.08] bg-[#1f2a3d] p-2"
            style={{ boxShadow: "0 16px 48px rgba(0,0,0,0.4)" }}
          >
            {/* Header — non-clickable */}
            <div className="mb-1 border-b border-white/[0.08] px-3 pb-3 pt-2">
              <p className="font-grotesk truncate text-[12px] text-white/95">
                {email ?? "—"}
              </p>
              <p className="font-grotesk mt-0.5 text-[10px] uppercase tracking-widest text-white/30">
                Operator Access
              </p>
            </div>

            {/* Sign out */}
            <button
              onClick={handleSignOut}
              className="flex w-full items-center gap-2.5 rounded-[8px] px-3 py-2.5 text-left transition-colors duration-150 hover:bg-[#2a3548]"
            >
              <LogOut className="h-[15px] w-[15px] shrink-0 text-white/55" />
              <span className="text-[13px] text-white/95">Sign out</span>
            </button>

            {/* Delete account */}
            <div className="mt-1 border-t border-white/[0.08] pt-2">
              <button
                onClick={() => {
                  setOpen(false);
                  setDeleteOpen(true);
                }}
                className="flex w-full items-center gap-2.5 rounded-[8px] px-3 py-2.5 text-left transition-colors duration-150 hover:bg-[#ef4444]/10"
              >
                <Trash2 className="h-[15px] w-[15px] shrink-0 text-[#ef4444]" />
                <span className="text-[13px] text-[#ef4444]">Delete account</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <DeleteAccountModal open={deleteOpen} onClose={() => setDeleteOpen(false)} />
    </>
  );
}
