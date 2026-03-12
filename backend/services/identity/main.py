"""
=============================================================================
Identity Service — Main Application
=============================================================================
Port: 8001
RUN: uvicorn main:app --port 8001 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv("../../../.env")  # Load .env before importing modules that need env vars

# Absolute imports — required for uvicorn which runs main.py as top-level
from database import engine                # noqa: E402
from devhub_shared.logging.logger import get_logger  # noqa: E402
from routers.auth import router as auth_router        # noqa: E402

logger = get_logger(__name__, service_name="identity")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Identity Service starting up", extra={"port": 8001})
    yield
    await engine.dispose()
    logger.info("Identity Service shut down")


app = FastAPI(
    title="Dev-Hub Identity Service",
    description="Authentication and user management. Internal service — not publicly exposed.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "identity", "version": "0.1.0"}


# Mount auth router
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
