import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

/**
 * Refreshes the Supabase auth session on every request.
 *
 * Returns the authenticated user (or null) alongside the response that
 * carries the refreshed session cookies. The caller (middleware.ts) uses
 * the user to apply redirect logic before returning the final response.
 *
 * IMPORTANT: always return `supabaseResponse` (or a response derived from
 * it) — never a plain NextResponse.next(). Returning a bare response would
 * drop the Set-Cookie headers that keep the session alive.
 */
export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          // Write updated cookies onto both the request (for downstream
          // middleware) and the response (to reach the browser).
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // getUser() validates the JWT with Supabase's server — never trust a
  // locally decoded token for auth decisions.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return { supabaseResponse, user };
}
