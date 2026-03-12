"""
=============================================================================
BFF (Backend for Frontend) — API Gateway
=============================================================================
Port: 8000 — The ONLY service the Next.js frontend communicates with.

RUN: uvicorn main:app --port 8000 --reload
=============================================================================
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv("../../.env")

# Absolute imports — must come after load_dotenv
from devhub_shared.logging.logger import get_logger  # noqa: E402
from routers.auth import router as auth_router        # noqa: E402

logger = get_logger(__name__, service_name="bff")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("BFF API Gateway starting up", extra={"port": 8000})
    yield
    logger.info("BFF API Gateway shutting down")


app = FastAPI(
    title="Dev-Hub BFF — API Gateway",
    description="Backend for Frontend: single entry point for the Next.js dashboard.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "bff", "version": "0.1.0"}


# Mount routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
