"""
=============================================================================
Identity Service — Auth Router
=============================================================================
Endpoints:
    POST /auth/register  → Create a new user account
    POST /auth/login     → Validate credentials, issue JWT pair
    GET  /auth/me        → Return current user from JWT

ARGON2 PASSWORD HASHING:
    Why not bcrypt (which most tutorials use)?
    The OWASP Password Storage Cheat Sheet (2023) recommends Argon2id as the
    first choice. Argon2 is:
    - Memory-hard: brute-forcing requires lots of RAM, not just CPU
    - The PHC (Password Hashing Competition) winner in 2015
    - Used by 1Password, Firefox, and Bitwarden

    Usage:
        ph = PasswordHasher()
        hash = ph.hash("raw_password")    # one-way hash
        ph.verify(hash, "raw_password")   # raises if wrong
=============================================================================
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from devhub_shared.auth.jwt_handler import create_access_token, create_refresh_token, decode_token, TokenInvalidError, TokenExpiredError
from devhub_shared.logging.logger import get_logger

from database import get_db
from models import User
from schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()
logger = get_logger(__name__, service_name="identity")

# Argon2 hasher with OWASP-recommended defaults:
# time_cost=3 (iterations), memory_cost=65536 (64MB), parallelism=4
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


# =============================================================================
# POST /auth/register
# =============================================================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Registration flow:
    1. Check if email is already taken (raise 409 if so)
    2. Hash the password with Argon2
    3. Insert new User row into identity.users
    4. Return the safe UserResponse (no password_hash)
    """
    # Step 1: Duplicate email check
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    # Step 2: Hash password — NEVER store raw password
    password_hash = ph.hash(payload.password)

    # Step 3: Create User ORM object and persist
    user = User(
        email=payload.email,
        display_name=payload.display_name,
        password_hash=password_hash,
    )
    db.add(user)
    await db.flush()   # flush to get the DB-assigned values (id, created_at)
                       # without committing yet (get_db dependency commits on success)

    logger.info("User registered", extra={"user_id": str(user.id), "email": user.email})

    # Step 4: Return safe response (Pydantic reads from ORM object via from_attributes=True)
    return UserResponse.model_validate(user)


# =============================================================================
# POST /auth/login
# =============================================================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT access + refresh tokens",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login flow:
    1. Find user by email
    2. Verify Argon2 hash matches the submitted password
    3. Issue access token (30 min) + refresh token (7 days)

    SECURITY: We return the same error for "email not found" and "wrong password".
    This prevents user enumeration attacks (attacker can't determine if email exists).
    """
    # Step 1: Look up user
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    # Step 2: Verify password
    # Note: We run verify even if user is None (dummy hash) to prevent
    # timing-based user enumeration attacks.
    try:
        if user is None:
            ph.verify("$argon2id$v=19$m=65536,t=3,p=4$dummy$dummydummydummydummydummy", payload.password)
        ph.verify(user.password_hash, payload.password)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Step 3: Issue JWT pair
    token_data = {"user_id": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"user_id": str(user.id)})

    logger.info("User logged in", extra={"user_id": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# =============================================================================
# GET /auth/me
# =============================================================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user's profile",
)
async def get_me(
    db: AsyncSession = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
) -> UserResponse:
    """
    Returns the profile of the currently authenticated user.

    DESIGN NOTE: This endpoint does NOT validate the JWT itself.
    The BFF validates the JWT *before* forwarding this request, then injects
    the user_id as the 'X-User-Id' header. This service trusts internal headers
    (it's on an internal network — not publicly accessible).

    This is the "internal trust" pattern: only the BFF calls this endpoint.
    """
    result = await db.execute(select(User).where(User.id == x_user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_validate(user)
