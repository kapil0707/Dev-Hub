"""
=============================================================================
JWT Handler — devhub_shared.auth.jwt_handler
=============================================================================
PURPOSE:
    Centralizes ALL JWT operations: token creation and decoding.
    All six services import from here — no duplication.

JWT ARCHITECTURE OVERVIEW:
    We use a TWO-TOKEN strategy (industry standard):

    1. ACCESS TOKEN (short-lived, 30 min default)
       - Sent with every API request in the Authorization header
       - Contains user identity payload (user_id, email, role)
       - Short lifetime limits the damage if a token is stolen

    2. REFRESH TOKEN (long-lived, 7 days default)
       - Sent only to /auth/refresh endpoint
       - Used to get a new access token without re-login
       - Stored in httpOnly cookie (not accessible by JavaScript)

    Token Flow:
        Login → get access_token + refresh_token
        API call → use access_token
        access_token expires → use refresh_token to get new access_token
        refresh_token expires → user must log in again

WHAT IS JWT?
    JWT = JSON Web Token. It has 3 parts (Base64 encoded, dot-separated):
        Header.Payload.Signature
    e.g.: eyJhbGci....eyJ1c2VyX2lk....SflKxwRJ...

    The SIGNATURE is what makes it tamper-proof — only our server knows the
    JWT_SECRET_KEY used to sign it. Verifying = re-computing the signature.

USAGE:
    from devhub_shared.auth.jwt_handler import create_access_token, decode_token
    token = create_access_token(data={"user_id": "...", "email": "..."})
    payload = decode_token(token)  # raises if expired or invalid
=============================================================================
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt


# Load from environment — set via .env file and load_dotenv()
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-insecure-key-replace-me")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenExpiredError(Exception):
    """Raised when a JWT has passed its expiration time."""


class TokenInvalidError(Exception):
    """Raised when a JWT signature is invalid or the token is malformed."""


def create_access_token(data: dict[str, Any]) -> str:
    """
    Creates a short-lived access JWT.

    Args:
        data: The payload to embed. Must contain 'user_id' and 'email'.
              Example: {"user_id": "uuid-here", "email": "user@example.com"}

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Creates a long-lived refresh JWT.

    Args:
        data: Minimal payload — typically just {"user_id": "uuid-here"}

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodes and validates a JWT.

    Raises:
        TokenExpiredError: If the token's 'exp' claim is in the past.
        TokenInvalidError: If the signature doesn't match or token is malformed.

    Returns:
        The decoded payload as a dictionary.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        error_str = str(e).lower()
        if "expired" in error_str:
            raise TokenExpiredError("JWT has expired") from e
        raise TokenInvalidError(f"JWT is invalid: {e}") from e
