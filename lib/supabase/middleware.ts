import { createServerClient } from "@supabase/ssr";
import { type NextRequest, NextResponse } from "next/server";

// Always return `supabaseResponse`, never a plain NextResponse.next() — bare responses
// drop the Set-Cookie headers that keep the session alive.
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

  // getUser() validates with Supabase's server — never trust a locally decoded token
  let user = null;
  try {
    const { data } = await supabase.auth.getUser();
    user = data.user;
  } catch (_error: unknown) {
    if (process.env.NODE_ENV === "development") {
      console.debug("Session refresh failed — redirecting to login");
    }
  }

  return { supabaseResponse, user };
}
