"""
=============================================================================
BFF — Auth Router (Cookie-Based JWT)
=============================================================================
POST /api/v1/auth/register  → proxy to Identity Service (returns user JSON)
POST /api/v1/auth/login     → proxy to Identity, SET httpOnly cookie with JWT
POST /api/v1/auth/logout    → clear the cookie
GET  /api/v1/auth/me        → protected; reads JWT from cookie, returns user
=============================================================================
"""
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from dependencies import get_current_user

router = APIRouter()

IDENTITY_SERVICE_URL = f"http://localhost:{os.getenv('IDENTITY_SERVICE_PORT', '8001')}"
COOKIE_NAME = "access_token"


# =============================================================================
# Helper: forward request body to Identity Service
# =============================================================================
async def _call_identity(method: str, path: str, body: bytes | None = None, headers: dict | None = None):
    """Call the Identity Service and return the httpx response."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(
                method=method,
                url=f"{IDENTITY_SERVICE_URL}{path}",
                content=body,
                headers=headers or {"Content-Type": "application/json"},
            )
        return resp
    except httpx.ConnectError:
        raise HTTPException(503, detail="Identity Service is unavailable")
    except httpx.TimeoutException:
        raise HTTPException(504, detail="Identity Service timed out")


# =============================================================================
# POST /register — public
# =============================================================================
@router.post("/register", summary="Register a new user")
async def register(request: Request):
    body = await request.body()
    resp = await _call_identity("POST", "/auth/register", body)
    return JSONResponse(content=resp.json(), status_code=resp.status_code)


# =============================================================================
# POST /login — public, sets httpOnly cookie
# =============================================================================
@router.post("/login", summary="Login and receive JWT via httpOnly cookie")
async def login(request: Request):
    """
    1. Forward credentials to Identity Service
    2. If 200: extract access_token from response JSON
    3. Set it as an httpOnly cookie on the response
    4. Return a safe JSON body (no token exposed to JS)
    """
    body = await request.body()
    resp = await _call_identity("POST", "/auth/login", body)

    if resp.status_code != 200:
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

    data = resp.json()
    access_token = data.get("access_token", "")

    # Build response — don't include the raw token in the body
    response = JSONResponse(
        content={"message": "Login successful", "token_type": "cookie"},
        status_code=200,
    )

    # Set httpOnly cookie
    # httponly=True  → JS cannot read this cookie (XSS protection)
    # samesite="lax" → cookie sent on same-site requests + top-level navigations
    # secure=False   → allow HTTP for localhost dev (set True in production)
    # max_age=1800   → 30 minutes (matches JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,       # CHANGE TO True IN PRODUCTION (requires HTTPS)
        max_age=1800,
        path="/",
    )
    return response


# =============================================================================
# POST /logout — clears the cookie
# =============================================================================
@router.post("/logout", summary="Clear auth cookie and log out")
async def logout():
    response = JSONResponse(content={"message": "Logged out"}, status_code=200)
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return response


# =============================================================================
# GET /me — protected (requires valid cookie)
# =============================================================================
@router.get("/me", summary="Get current user profile")
async def me(current_user: dict = Depends(get_current_user)):
    """
    JWT is decoded locally by get_current_user dependency.
    Then we call Identity Service /auth/me with X-User-Id header
    to get the full user profile from the database.
    """
    resp = await _call_identity(
        "GET",
        "/auth/me",
        headers={
            "Content-Type": "application/json",
            "X-User-Id": current_user["user_id"],
        },
    )
    return JSONResponse(content=resp.json(), status_code=resp.status_code)
