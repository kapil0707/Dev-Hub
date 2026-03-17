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

import { useEffect, useState } from "react";
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
  ShowChart as ChartIcon,
} from "@mui/icons-material";
import { useAuth } from "@/contexts/AuthContext";
import { DashboardMetrics, getDashboardMetrics, trackEvent } from "@/lib/api/analytics";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Legend
} from "recharts";

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [metricsLoading, setMetricsLoading] = useState(true);

  useEffect(() => {
    // Track page view once upon mount
    trackEvent("page_view", { page: "dashboard", source: "direct_navigation" });

    // Fetch the 7-day metrics
    getDashboardMetrics(7)
      .then((data) => setMetrics(data))
      .catch((err) => console.error("Failed to fetch dashboard metrics", err))
      .finally(() => setMetricsLoading(false));
  }, []);

  // Compute dynamic display values based on API or fallbacks
  const totalEvents = metrics?.summary?.total_events ?? 0;
  const activeUsers = metrics?.summary?.active_users ?? 0;
  // If the user hasn't made any events, show friendly zeroes
  
  const METRICS_CARDS = [
    {
      label: "Total Platform Events",
      value: metricsLoading ? "..." : totalEvents.toLocaleString(),
      icon: <ChartIcon sx={{ fontSize: 28 }} />,
      gradient: "linear-gradient(135deg, #06B6D4, #0891B2)",
      change: "Last 7 days",
    },
    {
      label: "Active Users",
      value: metricsLoading ? "..." : activeUsers.toLocaleString(),
      icon: <StorageIcon sx={{ fontSize: 28 }} />,
      gradient: "linear-gradient(135deg, #8B5CF6, #7C3AED)",
      change: "Last 7 days",
    },
    {
      label: "Snippets Run (Mock)",
      value: "Coming Soon",
      icon: <RunIcon sx={{ fontSize: 28 }} />,
      gradient: "linear-gradient(135deg, #F59E0B, #D97706)",
      change: "",
    },
    {
      label: "Success Rate (Mock)",
      value: "100%",
      icon: <SuccessIcon sx={{ fontSize: 28 }} />,
      gradient: "linear-gradient(135deg, #22C55E, #16A34A)",
      change: "System healthy",
    },
  ];

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
          Here&apos;s a live overview of your Dev-Hub activities.
        </Typography>
      </Box>

      {/* Metric Cards Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {METRICS_CARDS.map((metric) => (
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
              <Box sx={{ height: 4, background: metric.gradient }} />
              <CardContent sx={{ p: 3 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    background: `${metric.gradient}`,
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

                <Typography variant="h4" sx={{ fontWeight: 700, color: "#F1F5F9", mb: 0.5 }}>
                  {metric.value}
                </Typography>
                <Typography variant="body2" sx={{ color: "#94A3B8", fontWeight: 500, mb: 1 }}>
                  {metric.label}
                </Typography>
                <Typography variant="caption" sx={{ color: "#64748B" }}>
                  {metric.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* TimeSeries Area Chart */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card
            sx={{
              bgcolor: "rgba(30, 41, 59, 0.6)",
              border: "1px solid rgba(148, 163, 184, 0.08)",
              p: 3,
            }}
          >
            <Typography variant="h6" sx={{ color: "#F1F5F9", mb: 3 }}>
              Engagement Activity (Last 7 Days)
            </Typography>
            <Box sx={{ height: 300, width: "100%" }}>
              {metricsLoading ? (
                <Skeleton variant="rectangular" width="100%" height="100%" />
              ) : metrics && metrics.timeseries && metrics.timeseries.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={metrics.timeseries}>
                    <defs>
                      <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis 
                      dataKey="date" 
                      stroke="#94A3B8" 
                      tick={{ fill: '#94A3B8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis 
                      stroke="#94A3B8" 
                      tick={{ fill: '#94A3B8' }}
                      axisLine={false}
                      tickLine={false}
                      allowDecimals={false}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px' }}
                      itemStyle={{ color: '#06B6D4' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="count" 
                      stroke="#06B6D4" 
                      strokeWidth={3}
                      fillOpacity={1} 
                      fill="url(#colorCount)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                  <Typography variant="body1" color="#64748B">No analytics data available yet.</Typography>
                </Box>
              )}
            </Box>
          </Card>
        </Grid>

        {/* Breakdown by Event Type Bar Chart */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <Card
            sx={{
              bgcolor: "rgba(30, 41, 59, 0.6)",
              border: "1px solid rgba(148, 163, 184, 0.08)",
              p: 3,
              height: "100%"
            }}
          >
            <Typography variant="h6" sx={{ color: "#F1F5F9", mb: 3 }}>
              Activities By Type
            </Typography>
            <Box sx={{ height: 300, width: "100%" }}>
              {metricsLoading ? (
                <Skeleton variant="rectangular" width="100%" height="100%" />
              ) : metrics && metrics.by_type && metrics.by_type.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics.by_type} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="event_type" type="category" width={100} stroke="#94A3B8" tick={{ fill: '#94A3B8', fontSize: 12 }} />
                    <Tooltip 
                      cursor={{fill: 'rgba(255, 255, 255, 0.05)'}}
                      contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', borderRadius: '8px' }}
                    />
                    <Bar dataKey="count" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                  <Typography variant="body1" color="#64748B">Not enough data to display breakdown.</Typography>
                </Box>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
