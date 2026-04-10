import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

/**
 * Server-side Supabase client.
 * Call this inside Server Components, Route Handlers, and Server Actions.
 * Uses next/headers cookies() — do not call from Client Components.
 *
 * setAll is wrapped in try/catch because cookies cannot be mutated in
 * Server Components (read-only context). Mutations work in Route Handlers
 * and Server Actions where the response can be modified.
 */
export function createClient() {
  const cookieStore = cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => {
              cookieStore.set(name, value, options);
            });
          } catch {
            // Called from a Server Component — the session will be refreshed
            // by the middleware on the next request.
          }
        },
      },
    }
  );
}
