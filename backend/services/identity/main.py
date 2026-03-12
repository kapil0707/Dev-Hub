"""
=============================================================================
Identity Service — Authentication & User Management
=============================================================================
Port: 8001

RESPONSIBILITY:
    - User registration (create users with hashed passwords)
    - User login (validate credentials, issue JWTs)
    - Token refresh (exchange refresh token for new access token)
    - User profile retrieval

PROTOCOL: REST/JSON (called by BFF only — never directly by frontend)

DATABASE: PostgreSQL → schema: identity → table: identity.users

WHY IS PASSWORD HASHING DONE HERE AND NOT IN THE BFF?
    Each microservice is the "owner" of its domain. Identity owns passwords.
    The BFF should never touch raw passwords — it only relays the request.

RUN (with venv active):
    uvicorn main:app --port 8001 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from devhub_shared.logging.logger import get_logger

load_dotenv("../../../.env")

logger = get_logger(__name__, service_name="identity")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Identity Service starting up", extra={"port": 8001})
    # TODO (Phase 1): Initialize SQLAlchemy async engine here
    yield
    logger.info("Identity Service shutting down")


app = FastAPI(
    title="Dev-Hub Identity Service",
    description="Authentication and user management service.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "identity", "version": "0.1.0"}


# TODO (Phase 1): Implement these endpoints
# POST /auth/register → RegisterRequest(username, email, password) → UserResponse
# POST /auth/login    → LoginRequest(email, password) → TokenResponse
# POST /auth/refresh  → RefreshRequest(refresh_token) → TokenResponse
# GET  /auth/me       → (JWT validated by BFF, user_id passed as header) → UserResponse
