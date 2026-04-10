import { type NextRequest, NextResponse } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

// Routes that logged-in users should be bounced away from.
const AUTH_ROUTES = ["/login", "/signup"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Refresh the session and get the current user.
  // supabaseResponse carries any Set-Cookie headers needed to keep the
  // session alive — it must be returned (or its cookies forwarded) on
  // every code path.
  const { supabaseResponse, user } = await updateSession(request);

  // ── Redirect authenticated users away from auth pages ──────────────
  if (user && AUTH_ROUTES.includes(pathname)) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  // ── Redirect unauthenticated users away from protected pages ───────
  // Auth routes and the static file matcher below are public.
  // Everything else requires a session.
  if (!user && !AUTH_ROUTES.includes(pathname)) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     *   - _next/static  (static assets)
     *   - _next/image   (image optimisation)
     *   - favicon.ico
     *   - common static extensions
     */
    "/((?!_next/static|_next/image|favicon\\.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js)$).*)",
  ],
};
