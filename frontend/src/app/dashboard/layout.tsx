/**
 * =============================================================================
 * Dashboard Layout — Persistent Sidebar + Topbar
 * =============================================================================
 * This layout wraps ALL pages under /dashboard/*.
 * It provides:
 *   1. Sidebar (220px) — navigation links with icons
 *   2. Topbar (64px) — user greeting + avatar + logout
 *   3. Main content area — where {children} renders
 *
 * NEXT.JS LAYOUT PATTERN:
 *   /dashboard/layout.tsx → persistent shell
 *   /dashboard/page.tsx   → Overview (default child)
 *   /dashboard/snippets/page.tsx → Snippets (future Phase 3)
 *
 *   When navigating between dashboard pages, ONLY the children change —
 *   the sidebar and topbar stay mounted (no re-render, no flicker).
 * =============================================================================
 */
"use client";

import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  IconButton,
  Tooltip,
  Divider,
  Stack,
  Skeleton,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  SmartToy as AutomationIcon,
  Folder as FilesIcon,
  Logout as LogoutIcon,
  Terminal as TerminalIcon,
} from "@mui/icons-material";
import { useAuth } from "@/contexts/AuthContext";

const SIDEBAR_WIDTH = 240;

const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: <DashboardIcon /> },
  { label: "Snippets", href: "/dashboard/snippets", icon: <CodeIcon />, disabled: true },
  { label: "Automation", href: "/dashboard/automation", icon: <AutomationIcon />, disabled: false },
  { label: "Files", href: "/dashboard/files", icon: <FilesIcon />, disabled: false },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      {/* ================================================================= */}
      {/* SIDEBAR                                                           */}
      {/* ================================================================= */}
      <Drawer
        variant="permanent"
        sx={{
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: SIDEBAR_WIDTH,
            boxSizing: "border-box",
            bgcolor: "rgba(15, 23, 42, 0.95)",
            borderRight: "1px solid rgba(148, 163, 184, 0.08)",
            backdropFilter: "blur(20px)",
          },
        }}
      >
        {/* Brand logo */}
        <Stack
          direction="row"
          alignItems="center"
          spacing={1.5}
          sx={{ px: 2.5, py: 2.5 }}
        >
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 1.5,
              background: "linear-gradient(135deg, #06B6D4, #8B5CF6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <TerminalIcon sx={{ color: "#fff", fontSize: 20 }} />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: "#F1F5F9" }}>
            DevHub
          </Typography>
        </Stack>

        <Divider sx={{ borderColor: "rgba(148, 163, 184, 0.08)" }} />

        {/* Navigation Links */}
        <List sx={{ px: 1.5, py: 2 }}>
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <ListItemButton
                key={item.href}
                component={item.disabled ? "div" : Link}
                href={item.disabled ? undefined : item.href}
                disabled={item.disabled}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  px: 2,
                  py: 1.2,
                  color: isActive ? "#06B6D4" : "#94A3B8",
                  bgcolor: isActive ? "rgba(6, 182, 212, 0.08)" : "transparent",
                  "&:hover": {
                    bgcolor: isActive
                      ? "rgba(6, 182, 212, 0.12)"
                      : "rgba(148, 163, 184, 0.06)",
                  },
                  transition: "all 0.15s ease",
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 36,
                    color: isActive ? "#06B6D4" : "#64748B",
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: "0.875rem",
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
                {item.disabled && (
                  <Typography
                    variant="caption"
                    sx={{
                      bgcolor: "rgba(148, 163, 184, 0.1)",
                      color: "#64748B",
                      px: 1,
                      py: 0.25,
                      borderRadius: 1,
                      fontSize: "0.65rem",
                    }}
                  >
                    Soon
                  </Typography>
                )}
              </ListItemButton>
            );
          })}
        </List>
      </Drawer>

      {/* ================================================================= */}
      {/* MAIN AREA (Topbar + Content)                                      */}
      {/* ================================================================= */}
      <Box sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        {/* Topbar */}
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: "rgba(11, 17, 32, 0.8)",
            backdropFilter: "blur(12px)",
            borderBottom: "1px solid rgba(148, 163, 184, 0.08)",
          }}
        >
          <Toolbar sx={{ justifyContent: "flex-end", gap: 2 }}>
            {loading ? (
              <Skeleton width={120} height={24} />
            ) : user ? (
              <Stack direction="row" alignItems="center" spacing={2}>
                <Typography variant="body2" sx={{ color: "#94A3B8" }}>
                  {user.display_name}
                </Typography>
                <Avatar
                  src={user.avatar_url || undefined}
                  sx={{
                    width: 34,
                    height: 34,
                    bgcolor: "#06B6D4",
                    fontSize: "0.85rem",
                    fontWeight: 600,
                  }}
                >
                  {user.display_name?.charAt(0).toUpperCase()}
                </Avatar>
                <Tooltip title="Logout">
                  <IconButton
                    onClick={logout}
                    size="small"
                    sx={{ color: "#64748B", "&:hover": { color: "#EF4444" } }}
                  >
                    <LogoutIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Stack>
            ) : null}
          </Toolbar>
        </AppBar>

        {/* Page Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            bgcolor: "#0B1120",
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
}
