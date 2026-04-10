import { create } from "zustand";
import type { Session, User } from "@supabase/supabase-js";

import { createClient } from "@/lib/supabase/client";

export interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;

  setUser: (user: User | null) => void;
  setSession: (session: Session | null) => void;
  setLoading: (isLoading: boolean) => void;
  signOut: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()((set) => ({
  // ── Initial state ─────────────────────────────────────────────────
  user: null,
  session: null,
  isLoading: true, // true until initialize() completes

  // ── Setters ───────────────────────────────────────────────────────
  setUser: (user) => set({ user }),
  setSession: (session) => set({ session }),
  setLoading: (isLoading) => set({ isLoading }),

  // ── signOut ───────────────────────────────────────────────────────
  signOut: async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    // Clear local state; middleware will redirect to /login on next navigation.
    set({ user: null, session: null });
  },

  // ── initialize ────────────────────────────────────────────────────
  initialize: async () => {
    const supabase = createClient();

    // Hydrate from the existing session stored in the browser (fast, local).
    // The middleware uses getUser() (server-verified) for route protection;
    // getSession() here is only for populating UI state.
    const {
      data: { session },
    } = await supabase.auth.getSession();

    set({ session, user: session?.user ?? null });

    // Keep store in sync for the lifetime of the tab.
    supabase.auth.onAuthStateChange((_event, session) => {
      set({ session, user: session?.user ?? null });
    });

    set({ isLoading: false });
  },
}));
