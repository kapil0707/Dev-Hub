"""
=============================================================================
Identity Service — Pydantic Schemas (Request/Response Models)
=============================================================================
PURPOSE:
    Pydantic models serve as the validation and serialization layer between
    the HTTP request/response and your Python code.

    FastAPI uses these automatically:
    - Request body → Pydantic validates incoming JSON, raises 422 if invalid
    - Return value → Pydantic serializes Python objects to JSON

THE SEPARATION FROM ORM MODELS:
    You have TWO separate layers, each with a distinct job:
        SQLAlchemy Model (models.py)  → talks to the DATABASE
        Pydantic Schema  (schemas.py) → talks to the HTTP layer

    WHY TWO LAYERS? Because what you store ≠ what you expose:
    - DB stores `password_hash`; API should NEVER return it (security!)
    - DB stores internal fields (is_active); API may not want to expose those
    - API may accept a `password` field that gets hashed before storage

    This is the DTO (Data Transfer Object) pattern — standard in enterprise backends.
=============================================================================
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# =============================================================================
# Request Schemas (what the client sends IN)
# =============================================================================

class RegisterRequest(BaseModel):
    """Payload for POST /auth/register"""
    email: EmailStr                     # Pydantic validates email format automatically
    display_name: str = Field(
        min_length=2,
        max_length=100,
        description="Public display name",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="At least 8 characters",
    )

    @field_validator("password")
    @classmethod
    def password_not_common(cls, v: str) -> str:
        """Reject obviously weak passwords."""
        common = {"password", "12345678", "qwerty123", "password1"}
        if v.lower() in common:
            raise ValueError("Password is too common")
        return v


class LoginRequest(BaseModel):
    """Payload for POST /auth/login"""
    email: EmailStr
    password: str


# =============================================================================
# Response Schemas (what the server sends BACK)
# =============================================================================

class UserResponse(BaseModel):
    """
    Safe representation of a User — password_hash is intentionally excluded.

    model_config with from_attributes=True allows Pydantic to read from
    SQLAlchemy ORM objects directly (not just plain dicts).
    Without this, you'd have to manually convert ORM objects to dicts.
    """
    id: uuid.UUID
    email: str
    display_name: str
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}  # enables ORM → Pydantic conversion


class TokenResponse(BaseModel):
    """
    Returned after a successful login.
    Both tokens are JWTs — access_token is short-lived, refresh_token is long-lived.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"           # OAuth2 convention: always lowercase "bearer"


class ErrorResponse(BaseModel):
    """Standardized error shape — consistent across all endpoints."""
    detail: str
