/**
 * =============================================================================
 * MUI Theme — Dev-Hub Dark Mode
 * =============================================================================
 * Creates a polished dark theme with Deep Navy + Cyan accents.
 * This file is imported by the root layout and wrapped in ThemeProvider.
 *
 * WHY A CUSTOM THEME?
 *   MUI defaults are functional but generic. A curated palette makes the
 *   app feel premium — like Vercel, Linear, or Raycast dashboards.
 *
 * COLOR SYSTEM:
 *   Background: Deep Navy (#0B1120, #111827)
 *   Surface/Cards: Slightly lighter navy (#1E293B)
 *   Primary accent: Cyan (#06B6D4) — eye-catching without being harsh
 *   Secondary: Violet (#8B5CF6) — for secondary actions
 *   Text: High-contrast white with subtle gray for secondary
 * =============================================================================
 */
"use client";

import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#06B6D4",       // Cyan 500
      light: "#22D3EE",      // Cyan 400
      dark: "#0891B2",       // Cyan 600
      contrastText: "#0B1120",
    },
    secondary: {
      main: "#8B5CF6",       // Violet 500
      light: "#A78BFA",      // Violet 400
      dark: "#7C3AED",       // Violet 600
    },
    background: {
      default: "#0B1120",    // Deep navy — the darkest background
      paper: "#1E293B",      // Card/surface background
    },
    text: {
      primary: "#F1F5F9",    // Slate 100
      secondary: "#94A3B8",  // Slate 400
    },
    divider: "rgba(148, 163, 184, 0.12)",
    error: {
      main: "#EF4444",       // Red 500
    },
    success: {
      main: "#22C55E",       // Green 500
    },
    warning: {
      main: "#F59E0B",       // Amber 500
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    h4: {
      fontWeight: 700,
      letterSpacing: "-0.02em",
    },
    h5: {
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    h6: {
      fontWeight: 600,
    },
    body2: {
      color: "#94A3B8",
    },
  },
  shape: {
    borderRadius: 12,         // Rounded corners everywhere
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",   // No ALL CAPS buttons — modern convention
          fontWeight: 600,
          borderRadius: 8,
          padding: "10px 24px",
        },
        containedPrimary: {
          background: "linear-gradient(135deg, #06B6D4 0%, #0891B2 100%)",
          "&:hover": {
            background: "linear-gradient(135deg, #22D3EE 0%, #06B6D4 100%)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",   // Remove MUI's default paper overlay
          border: "1px solid rgba(148, 163, 184, 0.08)",
          backdropFilter: "blur(12px)",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
          },
        },
      },
    },
  },
});

export default theme;
