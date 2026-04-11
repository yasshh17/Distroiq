"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, LogOut, Trash2 } from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DeleteAccountModal } from "@/components/features/auth/DeleteAccountModal";
import { createClient } from "@/lib/supabase/client";

export function UserChip() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);

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
    <>
      <div className="flex items-center gap-3">
        {/* Pulsing status dot */}
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
        </span>

        {displayEmail && (
          <span
            className="text-[12.5px]"
            style={{ color: "rgba(255,255,255,0.8)" }}
          >
            {displayEmail}
          </span>
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-0.5 font-mono text-[11px] text-slate-400 transition-colors hover:text-white">
              Account
              <ChevronDown className="h-3 w-3" />
            </button>
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuItem
              onClick={handleSignOut}
              className="cursor-pointer gap-2 text-[13px]"
            >
              <LogOut className="h-3.5 w-3.5" />
              Sign out
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem
              onClick={() => setDeleteOpen(true)}
              className="cursor-pointer gap-2 text-[13px] text-red-500 focus:text-red-500"
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete account
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <DeleteAccountModal open={deleteOpen} onClose={() => setDeleteOpen(false)} />
    </>
  );
}
