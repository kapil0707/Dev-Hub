"""
=============================================================================
BFF — FastAPI Dependencies
=============================================================================
get_current_user: Validates JWT from Authorization header and extracts user_id.

DESIGN CHANGE from original plan:
    The original plan called the Identity Service /auth/me to validate the token.
    This creates a circular proxy dependency and extra network hop.

    Better approach: DECODE THE JWT LOCALLY in the BFF using the shared jwt_handler.
    - The JWT was signed by the Identity Service using JWT_SECRET_KEY
    - The BFF reads the same JWT_SECRET_KEY from .env
    - Decoding locally is instant — no extra HTTP call needed
    - The decode function raises exceptions for expired/invalid tokens

    The Identity Service /auth/me is then called ONLY when real DB data is needed
    (e.g., fetching the full user profile for the /me endpoint).
=============================================================================
"""
import os

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from devhub_shared.auth.jwt_handler import TokenExpiredError, TokenInvalidError, decode_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Decode + validate the JWT locally.
    Returns the token payload dict (contains user_id, email, exp, etc).

    Raises HTTP 401 for missing/expired/invalid tokens.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired — please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )
