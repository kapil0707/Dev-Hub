/**
 * =============================================================================
 * Dashboard Overview — /dashboard
 * =============================================================================
 * The default dashboard page showing:
 *   1. Greeting header with user's name
 *   2. 4 metric cards in a responsive grid
 *
 * METRIC CARDS:
 *   - Total Snippets
 *   - Storage Used
 *   - Scripts Run (Today)
 *   - Success Rate
 *
 *   For Phase 2, these show PLACEHOLDER data. Real data is wired in Phase 6
 *   when the Analytics Service is built.
 *
 * DESIGN:
 *   Each card has a gradient top accent strip, an icon, a large number,
 *   and a label. The grid is responsive: 4 columns on desktop, 2 on
 *   tablet, 1 on mobile.
 * =============================================================================
 */
"use client";

import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Skeleton,
} from "@mui/material";
import {
  Code as CodeIcon,
  Storage as StorageIcon,
  PlayArrow as RunIcon,
  CheckCircle as SuccessIcon,
} from "@mui/icons-material";
import { useAuth } from "@/contexts/AuthContext";

// Static placeholder data — replaced with real API calls in Phase 6
const METRICS = [
  {
    label: "Total Snippets",
    value: "24",
    icon: <CodeIcon sx={{ fontSize: 28 }} />,
    gradient: "linear-gradient(135deg, #06B6D4, #0891B2)",
    change: "+3 this week",
  },
  {
    label: "Storage Used",
    value: "128 MB",
    icon: <StorageIcon sx={{ fontSize: 28 }} />,
    gradient: "linear-gradient(135deg, #8B5CF6, #7C3AED)",
    change: "of 5 GB",
  },
  {
    label: "Scripts Run Today",
    value: "7",
    icon: <RunIcon sx={{ fontSize: 28 }} />,
    gradient: "linear-gradient(135deg, #F59E0B, #D97706)",
    change: "+2 vs yesterday",
  },
  {
    label: "Success Rate",
    value: "96%",
    icon: <SuccessIcon sx={{ fontSize: 28 }} />,
    gradient: "linear-gradient(135deg, #22C55E, #16A34A)",
    change: "Last 30 days",
  },
];

export default function DashboardPage() {
  const { user, loading } = useAuth();

  return (
    <Box>
      {/* Greeting */}
      <Box sx={{ mb: 4 }}>
        {loading ? (
          <Skeleton width={300} height={40} />
        ) : (
          <Typography variant="h4" sx={{ color: "#F1F5F9" }}>
            Welcome back,{" "}
            <Box component="span" sx={{ color: "#06B6D4" }}>
              {user?.display_name || "Developer"}
            </Box>
          </Typography>
        )}
        <Typography variant="body2" sx={{ mt: 0.5, color: "#64748B" }}>
          Here&apos;s what&apos;s happening with your projects.
        </Typography>
      </Box>

      {/* Metric Cards Grid */}
      <Grid container spacing={3}>
        {METRICS.map((metric) => (
          <Grid key={metric.label} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card
              sx={{
                bgcolor: "rgba(30, 41, 59, 0.6)",
                border: "1px solid rgba(148, 163, 184, 0.08)",
                overflow: "hidden",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: "0 12px 40px -15px rgba(0, 0, 0, 0.3)",
                },
              }}
            >
              {/* Gradient accent strip at the top */}
              <Box
                sx={{
                  height: 4,
                  background: metric.gradient,
                }}
              />
              <CardContent sx={{ p: 3 }}>
                {/* Icon */}
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    background: `${metric.gradient.replace("135deg", "135deg")}`,
                    opacity: 0.15,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    position: "relative",
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      position: "absolute",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: metric.gradient.includes("#06B6D4")
                        ? "#06B6D4"
                        : metric.gradient.includes("#8B5CF6")
                        ? "#8B5CF6"
                        : metric.gradient.includes("#F59E0B")
                        ? "#F59E0B"
                        : "#22C55E",
                    }}
                  >
                    {metric.icon}
                  </Box>
                </Box>

                {/* Value */}
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: "#F1F5F9",
                    lineHeight: 1,
                    mb: 0.5,
                  }}
                >
                  {metric.value}
                </Typography>

                {/* Label */}
                <Typography
                  variant="body2"
                  sx={{ color: "#94A3B8", fontWeight: 500, mb: 1 }}
                >
                  {metric.label}
                </Typography>

                {/* Subtext */}
                <Typography
                  variant="caption"
                  sx={{ color: "#64748B" }}
                >
                  {metric.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
