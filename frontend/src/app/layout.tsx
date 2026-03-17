/**
 * =============================================================================
 * Root Layout — Next.js App Router
 * =============================================================================
 * This is the top-level layout rendered for EVERY page in the app.
 * It sets up:
 *   1. Google Fonts (Inter) via next/font
 *   2. MUI ThemeProvider with our custom dark theme
 *   3. CssBaseline — MUI's CSS reset (normalizes browser defaults)
 *   4. AuthProvider — app-wide auth state
 *
 * LEARNING NOTE:
 *   In Next.js App Router, layout.tsx files create "persistent shells"
 *   that DON'T re-render when navigating between pages. Only the
 *   {children} slot changes — the layout shell stays mounted.
 * =============================================================================
 */
import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Inter } from "next/font/google";
import theme from "@/theme";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",        // Show fallback font immediately, swap when loaded
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Dev-Hub — Universal Developer Dashboard",
  description:
    "Manage code snippets, automate scripts, store files, and track analytics — all in one place.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body style={{ margin: 0, backgroundColor: "#0B1120" }} suppressHydrationWarning>
        <AppRouterCacheProvider options={{ key: "mui" }}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>
              {children}
            </AuthProvider>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
