import { createBrowserClient } from "@supabase/ssr";

/**
 * Browser-side Supabase client.
 * Call this inside Client Components ("use client").
 * Creates a new instance per call — safe because createBrowserClient
 * is memoised internally and reuses the same underlying GoTrue client.
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
