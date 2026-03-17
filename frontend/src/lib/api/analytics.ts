const BFF_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface TimeSeriesDataPoint {
  date: string;
  count: number;
}

export interface DashboardMetrics {
  summary: {
    total_events: number;
    active_users: number;
  };
  timeseries: TimeSeriesDataPoint[];
  by_type: {
    event_type: string;
    count: number;
  }[];
}

export async function getDashboardMetrics(days: number = 7): Promise<DashboardMetrics> {
  const res = await fetch(`${BFF_URL}/analytics/metrics?days=${days}`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch dashboard metrics");
  }
  return res.json();
}

export async function trackEvent(eventType: string, payload?: any) {
  try {
    await fetch(`${BFF_URL}/analytics/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        event_type: eventType,
        payload: payload,
      }),
    });
  } catch (error) {
    // Analytics failures should never crash the app
    console.error("Analytics tracking failed:", error);
  }
}
