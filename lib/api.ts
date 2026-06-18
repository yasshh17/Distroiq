import axios, { type AxiosError } from "axios";

import { useAuthStore } from "@/stores/auth";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// typeof window guard keeps this safe if api.ts is ever imported in a Server Component
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const session = useAuthStore.getState().session;
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  }
  return config;
});

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

// Pings the health endpoint every 10 minutes to prevent Render free-tier spin-down
export function startKeepAlive() {
  const ping = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/health`);
    } catch {}
  };
  ping();
  setInterval(ping, 10 * 60 * 1000);
}
