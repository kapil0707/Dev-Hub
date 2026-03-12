"""
=============================================================================
Analytics Service — Metrics and Event Aggregation
=============================================================================
Port: 8005

RESPONSIBILITY:
    - Ingests events from the BFF (e.g., "snippet_created", "script_executed")
    - Aggregates data for the Next.js dashboard charts
    - Provides time-series and summary statistics

EVENT-DRIVEN DESIGN NOTE:
    Rather than each service writing analytics directly, the BFF emits events
    to this service after successful operations. This decouples the analytics
    concern from business logic. The Analytics Service owns all reporting data.

DATABASE: PostgreSQL → schema: analytics → tables: analytics.events, analytics.daily_stats

RUN: uvicorn main:app --port 8005 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from devhub_shared.logging.logger import get_logger

load_dotenv("../../../.env")
logger = get_logger(__name__, service_name="analytics")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analytics Service starting up", extra={"port": 8005})
    yield
    logger.info("Analytics Service shutting down")


app = FastAPI(
    title="Dev-Hub Analytics Service",
    description="Event ingestion and metrics aggregation for the dashboard.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "analytics", "version": "0.1.0"}

# TODO (Phase 6):
# POST /events                        → EventRequest → 202 Accepted
# GET  /analytics/summary             → DashboardSummaryResponse
# GET  /analytics/executions/daily    → List[DailyExecutionPoint] (30-day series)
