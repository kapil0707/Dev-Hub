/**
 * =============================================================================
 * Root Page — /
 * =============================================================================
 * Redirects to /dashboard. If the user has no cookie, the Next.js
 * Edge Middleware will intercept and redirect to /login instead.
 * =============================================================================
 */
import { redirect } from "next/navigation";

export default function HomePage() {
  redirect("/dashboard");
}
