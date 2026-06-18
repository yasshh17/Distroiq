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
  user: null,
  session: null,
  isLoading: true,

  setUser: (user) => set({ user }),
  setSession: (session) => set({ session }),
  setLoading: (isLoading) => set({ isLoading }),

  signOut: async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    set({ user: null, session: null });
  },

  initialize: async () => {
    const supabase = createClient();

    // getSession() is fast/local; the middleware uses getUser() (server-verified) for route protection.
    const {
      data: { session },
    } = await supabase.auth.getSession();

    set({ session, user: session?.user ?? null });

    supabase.auth.onAuthStateChange((_event, session) => {
      set({ session, user: session?.user ?? null });
    });

    set({ isLoading: false });
  },
}));
