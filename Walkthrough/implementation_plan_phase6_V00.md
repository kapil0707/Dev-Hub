# Phase 6: Analytics Service + Dashboard Charts — Implementation Plan

This plan outlines the architecture and implementation steps for a dedicated Analytics microservice, its integration into the API Gateway (BFF), and the frontend dashboard visualization.

## Proposed Changes

---

### Backend: Analytics Service (Port 8005)

A new FastAPI microservice responsible for ingesting, storing, and aggregating telemetry/event data.

#### [NEW] `backend/services/analytics/alembic.ini` and `alembic/`
- Initialize Alembic for async migrations against an `analytics` schema in PostgreSQL.

#### [NEW] `backend/services/analytics/database.py`
- Setup SQLAlchemy async engine and [get_db](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/identity/database.py#71-90) dependency.

#### [NEW] `backend/services/analytics/models.py`
- Define `EventRecord` SQLAlchemy model mapping to `analytics.events` table.
- Columns: [id](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/contexts/AuthContext.tsx#44-102) (UUID), `user_id` (UUID, nullable), `event_type` (String, e.g., 'page_view', 'login', 'file_upload'), `payload` (JSONB), `timestamp` (DateTime).

#### [NEW] `backend/services/analytics/schemas.py`
- Pydantic models: `EventCreate`, `EventResponse`, `MetricSummary`, `TimeSeriesDataPoint`.

#### [NEW] `backend/services/analytics/routers/events.py`
- `POST /events`: Ingests a new event and stores it in the database.
- `GET /metrics/summary`: Returns simple aggregations (e.g., total requests, recent active users, event counts by type).
- `GET /metrics/timeseries`: Returns time-series aggregated data (e.g., events per day for the last 7 days) suitable for chart rendering.

#### [NEW] [backend/services/analytics/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/analytics/main.py)
- Initialize FastAPI app and include the `events` router.

---

### Backend: BFF API Gateway (Port 8000)

The API Gateway will expose the Analytics Service to the frontend securely.

#### [NEW] `backend/bff/routers/analytics.py`
- Define proxy endpoints forwarding `/api/v1/analytics/*` to `http://127.0.0.1:8005/*`.
- Inject `X-User-Id` header from the authenticated JWT token for the metrics queries to ensure users can only see their own metrics or general anonymized metrics.

#### [MODIFY] [backend/bff/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/main.py)
- Include the `analytics_router` to expose the new endpoints.

---

### Frontend: Next.js Dashboard

The user interface down on the existing Overview page will be updated to display real charts using the fetching data.

#### [NEW] `frontend/src/lib/api/analytics.ts`
- Functions: `trackEvent(eventType: string, payload?: any)`, `getSummaryMetrics()`, `getTimeSeriesData()` fetching from the BFF.

#### [MODIFY] [frontend/src/app/dashboard/page.tsx](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/app/dashboard/page.tsx)
- Replace the static placeholder dashboard with interactive charts.
- Install `recharts` (a popular React charting library) to visualize the `getTimeSeriesData()` response.
- Render dynamic Summary Cards populated by `getSummaryMetrics()`.

#### [MODIFY] [frontend/src/app/layout.tsx](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/app/layout.tsx) (or similar global scope)
- Add a simple global route watcher or hook to trigger generic `page_view` events to the analytics ingestion endpoint.

---

## Verification Plan

### Automated / Backend Tests
1. Verify the `analytics` PostgreSQL schema and `events` table are created successfully.
2. Direct API POST requests to `localhost:8005/events` to ensure data ingestion works.

### Manual Verification
1. Start all services. Navigate through the frontend (login, view snippets, upload files) to organically generate events.
2. View the **Overview** dashboard page and verify that the Summary Cards and Charts display the ingested events accurately.
3. Validate that existing functionality (auth, snippets, files, automation) remains completely unaffected by the new analytics asynchronous calls.
