"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, TriangleAlert } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createClient } from "@/lib/supabase/client";
import api from "@/lib/api";

interface DeleteAccountModalProps {
  open: boolean;
  onClose: () => void;
}

export function DeleteAccountModal({ open, onClose }: DeleteAccountModalProps) {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  function handleClose() {
    if (isLoading) return;
    setStep(1);
    setPassword("");
    setError(null);
    onClose();
  }

  async function handleDelete() {
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setIsLoading(true);
    setError(null);

    const supabase = createClient();

    // Step a — re-verify password
    const { data: userData } = await supabase.auth.getUser();
    const email = userData.user?.email;

    if (!email) {
      setError("Could not retrieve your account. Please sign in again.");
      setIsLoading(false);
      return;
    }

    const { error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (signInError) {
      setError("Incorrect password. Please try again.");
      setIsLoading(false);
      return;
    }

    // Step b — delete via backend (uses service role key)
    try {
      await api.delete("/api/v1/auth/account");
    } catch {
      setError("Failed to delete account. Please try again.");
      setIsLoading(false);
      return;
    }

    // Step c — sign out and redirect
    await supabase.auth.signOut();
    router.push("/login?deleted=true");
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && handleClose()}>
      <DialogContent className="sm:max-w-[420px]">
        {step === 1 ? (
          <>
            <DialogHeader>
              <div className="mb-1 flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
                <TriangleAlert className="h-5 w-5 text-red-600" />
              </div>
              <DialogTitle className="text-slate-800">
                Delete your account
              </DialogTitle>
              <DialogDescription className="text-[13.5px] leading-relaxed text-slate-500">
                This will permanently delete your account and all associated
                data. <span className="font-semibold text-slate-700">This cannot be undone.</span>
              </DialogDescription>
            </DialogHeader>

            <DialogFooter className="mt-2 gap-2 sm:gap-2">
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => setStep(2)}
                className="flex-1"
              >
                Continue
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="text-slate-800">
                Confirm deletion
              </DialogTitle>
              <DialogDescription className="text-[13.5px] text-slate-500">
                Enter your password to permanently delete your account.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-1.5 py-2">
              <label
                htmlFor="delete-confirm-password"
                className="block font-mono text-[10.5px] font-semibold uppercase tracking-wider text-slate-500"
              >
                Password
              </label>
              <Input
                id="delete-confirm-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                disabled={isLoading}
              />

              {error !== null && (
                <p className="rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-[12.5px] text-red-600">
                  {error}
                </p>
              )}
            </div>

            <DialogFooter className="gap-2 sm:gap-2">
              <Button
                variant="outline"
                onClick={handleClose}
                disabled={isLoading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting…
                  </>
                ) : (
                  "Delete my account"
                )}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
