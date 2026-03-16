"""
=============================================================================
BFF — FastAPI Dependencies (Cookie-Based JWT Auth)
=============================================================================
DESIGN: httpOnly cookies instead of Authorization headers.

WHY COOKIES OVER HEADERS FOR BROWSERS?
    Authorization: Bearer headers must be stored in JavaScript (localStorage
    or sessionStorage). Any XSS vulnerability can steal the token.

    httpOnly cookies CANNOT be read by JavaScript — the browser sends them
    automatically on every request. Even if an XSS attack executes JS,
    it cannot extract the cookie value.

    Trade-off: cookies require CSRF protection. We mitigate this with
    SameSite=Lax (blocks cross-origin POSTs from other sites).
=============================================================================
"""
from fastapi import Depends, HTTPException, Request, status

from devhub_shared.auth.jwt_handler import (
    TokenExpiredError,
    TokenInvalidError,
    decode_token,
)

COOKIE_NAME = "access_token"


async def get_current_user(request: Request) -> dict:
    """
    Read JWT from httpOnly cookie, decode it, return the payload.
    Raises HTTP 401 if cookie is missing, expired, or invalid.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — no access_token cookie",
        )
    try:
        payload = decode_token(token)
        return payload
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired — please log in again",
        )
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
        )
