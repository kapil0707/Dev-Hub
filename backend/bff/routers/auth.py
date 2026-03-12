"""
=============================================================================
BFF — Auth Router (Proxy to Identity Service)
=============================================================================
PURPOSE:
    The BFF acts as a PROXY for all auth-related requests.
    The frontend calls the BFF; BFF forwards to the Identity Service.

    Frontend sees:  POST /api/v1/auth/login   (BFF endpoint)
    BFF calls:      POST http://localhost:8001/auth/login  (Identity Service)

WHY PROXY INSTEAD OF DIRECT CALLS?
    1. The frontend only knows about ONE host: the BFF (port 8000)
    2. Internal service ports (8001-8005) are never exposed to the frontend
    3. The BFF can add security headers, rate limiting, and logging centrally
    4. If the Identity Service moves to a different host/port, only the BFF config changes

HTTPX ASYNC CLIENT:
    We use httpx (not requests) because requests is synchronous.
    A synchronous HTTP call inside an async FastAPI handler would block
    the entire event loop — causing all other requests to pause.
    httpx is the async equivalent of requests.
=============================================================================
"""
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from dependencies import get_current_user

router = APIRouter()

IDENTITY_SERVICE_URL = f"http://localhost:{os.getenv('IDENTITY_SERVICE_PORT', '8001')}"


async def _forward_to_identity(
    method: str,
    path: str,
    request: Request,
    extra_headers: dict | None = None,
) -> Response:
    """
    Generic helper that forwards a request to the Identity Service.
    Copies: method, headers (except host), body, and query params.

    Returns a FastAPI Response with the same status code and body.
    """
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header — it's for the BFF, not identity svc
    if extra_headers:
        headers.update(extra_headers)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(
                method=method,
                url=f"{IDENTITY_SERVICE_URL}{path}",
                content=body,
                headers=headers,
                params=dict(request.query_params),
            )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except httpx.ConnectError:
        raise HTTPException(503, detail="Identity Service is unavailable")
    except httpx.TimeoutException:
        raise HTTPException(504, detail="Identity Service timed out")


# =============================================================================
# Public endpoints (no JWT required)
# =============================================================================

@router.post("/register", summary="Register a new user")
async def register(request: Request) -> Response:
    """Proxy to Identity Service POST /auth/register"""
    return await _forward_to_identity("POST", "/auth/register", request)


@router.post("/login", summary="Login and receive JWT tokens")
async def login(request: Request) -> Response:
    """Proxy to Identity Service POST /auth/login"""
    return await _forward_to_identity("POST", "/auth/login", request)


# =============================================================================
# Protected endpoints (JWT required via get_current_user dependency)
# =============================================================================

@router.get("/me", summary="Get current user profile")
async def me(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Response:
    """
    Protected endpoint: JWT is validated by get_current_user dependency first.
    Then forwards to Identity Service with X-User-Id header injected.

    The Identity Service's /auth/me uses X-User-Id (not JWT) — it trusts
    that the BFF already validated the token.
    """
    return await _forward_to_identity(
        "GET",
        "/auth/me",
        request,
        extra_headers={"X-User-Id": current_user["user_id"]},
    )
