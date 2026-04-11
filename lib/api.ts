import axios, { type AxiosError } from "axios";

import { useAuthStore } from "@/stores/auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ── Request interceptor ───────────────────────────────────────────────
// Attach the current session's access token to every outgoing request.
// Reads from the Zustand store via getState() — works outside React.
// The typeof window guard keeps this safe if api.ts is ever imported
// in a Server Component context (no browser store available there).

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const session = useAuthStore.getState().session;
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  }
  return config;
});

// ── Response interceptor ──────────────────────────────────────────────
// On 401, the session has expired or been revoked. Sign the user out so
// the store is cleared and the middleware redirects them to /login on
// the next navigation.

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      await useAuthStore.getState().signOut();
    }
    return Promise.reject(error);
  }
);

export default api;

// ── Keep-alive ────────────────────────────────────────────────────────
// Pings the backend health endpoint every 10 minutes to prevent
// Render free-tier instances from spinning down between requests.

export function startKeepAlive() {
  const ping = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`);
    } catch {}
  };
  ping(); // immediate ping on load
  setInterval(ping, 10 * 60 * 1000); // every 10 min
}
