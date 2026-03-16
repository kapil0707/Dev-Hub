/**
 * =============================================================================
 * Next.js Edge Middleware — Route Protection
 * =============================================================================
 * This file runs on the EDGE (before the page renders) for every matched route.
 *
 * HOW IT WORKS:
 *   1. Middleware checks for the `access_token` cookie
 *   2. If the cookie exists → allow the request through
 *   3. If NO cookie + accessing /dashboard/* → redirect to /login
 *   4. If HAS cookie + accessing /login → redirect to /dashboard
 *
 * WHY EDGE MIDDLEWARE instead of client-side checks?
 *   Client-side: page loads, JS runs, THEN redirects → flash of content
 *   Edge middleware: redirect happens BEFORE the page is even sent → instant
 *
 * NOTE: This does NOT validate the JWT signature — only checks cookie existence.
 * The actual JWT validation happens on the BFF when API calls are made.
 * This is a UX optimization, not a security boundary.
 * =============================================================================
 */
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const COOKIE_NAME = "access_token";
const LOGIN_PATH = "/login";
const DASHBOARD_PATH = "/dashboard";

export function middleware(request: NextRequest) {
  const token = request.cookies.get(COOKIE_NAME);
  const { pathname } = request.nextUrl;

  // Protected routes: /dashboard and all sub-paths
  const isProtectedRoute = pathname.startsWith(DASHBOARD_PATH);
  // Auth routes: /login
  const isAuthRoute = pathname === LOGIN_PATH;

  // Case 1: No token + trying to access dashboard → redirect to login
  if (isProtectedRoute && !token) {
    const loginUrl = new URL(LOGIN_PATH, request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Case 2: Has token + on login page → redirect to dashboard
  if (isAuthRoute && token) {
    const dashboardUrl = new URL(DASHBOARD_PATH, request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  // Case 3: Allow through
  return NextResponse.next();
}

// Only run middleware on these paths (don't run on API routes, static files, etc.)
export const config = {
  matcher: ["/dashboard/:path*", "/login"],
};
