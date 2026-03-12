"""
=============================================================================
BFF (Backend for Frontend) — API Gateway
=============================================================================
Port: 8000

ARCHITECTURAL ROLE:
    The BFF is the only service that the Next.js frontend can talk to.
    The frontend knows NOTHING about the 5 downstream microservices.

    ALL requests from the frontend come here first. The BFF's job is to:
    1. Validate the JWT on every protected request
    2. Route the request to the appropriate microservice
    3. Aggregate responses if needed (combine data from multiple services)
    4. Return a clean, frontend-optimized JSON response

    This is the "Facade" pattern: one clean interface over a complex backend.

RUN (with venv active):
    uvicorn main:app --port 8000 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devhub_shared.logging.logger import get_logger

# Load environment variables from .env file at monorepo root
load_dotenv("../../.env")

logger = get_logger(__name__, service_name="bff")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan: code before 'yield' runs at startup, after yield at shutdown.
    This replaces the deprecated @app.on_event("startup") approach.
    """
    logger.info("BFF API Gateway starting up", extra={"port": 8000})
    yield
    logger.info("BFF API Gateway shutting down")


app = FastAPI(
    title="Dev-Hub BFF — API Gateway",
    description="Backend for Frontend: single entry point for the Next.js dashboard.",
    version="0.1.0",
    lifespan=lifespan,
)

# =============================================================================
# CORS Middleware
# =============================================================================
# WHAT IS CORS?
#   Cross-Origin Resource Sharing. Browsers block requests from one origin
#   (http://localhost:3000) to a different origin (http://localhost:8000)
#   by default. We must explicitly allow the frontend's origin here.
#
# WHY is allow_credentials=True important?
#   Because httpOnly cookies (which carry our JWT) require credentials mode.
# =============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only our Next.js dev server
    allow_credentials=True,                   # Required for httpOnly cookie JWT
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Routes
# =============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint. Used by:
    - Docker health checks
    - Load balancers
    - Your dev-start.ps1 script to verify service is running
    """
    return {"status": "ok", "service": "bff", "version": "0.1.0"}


# TODO (Phase 1): Mount auth router
# from routers.auth import router as auth_router
# app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

# TODO (Phase 3): Mount snippets router
# from routers.snippets import router as snippets_router
# app.include_router(snippets_router, prefix="/api/v1/snippets", tags=["Snippets"])
