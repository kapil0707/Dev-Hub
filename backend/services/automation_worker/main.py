"""
=============================================================================
Automation Worker — Local Script Execution Service
=============================================================================
Port: 8003

RESPONSIBILITY:
    Executes local shell scripts/commands on the developer's machine via Python
    subprocess. Records execution metadata to PostgreSQL for the dashboard.

SAFETY NOTE:
    This service executes arbitrary shell commands — it is ONLY safe because
    this is a localhost-only, single-user application. In a real multi-tenant
    system, you would sandbox scripts (Docker containers, seccomp profiles, etc.).

DATABASE: PostgreSQL → schema: automation → table: automation.executions

RUN: uvicorn main:app --port 8003 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from devhub_shared.logging.logger import get_logger

load_dotenv("../../../.env")
logger = get_logger(__name__, service_name="automation_worker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Automation Worker starting up", extra={"port": 8003})
    yield
    logger.info("Automation Worker shutting down")


app = FastAPI(
    title="Dev-Hub Automation Worker",
    description="Executes local shell scripts via subprocess.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "automation_worker", "version": "0.1.0"}

from routers.scripts import router as scripts_router
app.include_router(scripts_router, prefix="/scripts")
