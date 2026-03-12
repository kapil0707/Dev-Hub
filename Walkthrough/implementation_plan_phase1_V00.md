# Phase 1: Identity Service + BFF Auth

## Goal
Build a complete, working authentication system. By the end of this phase:
- `POST /api/v1/auth/register` creates a user with a hashed password in PostgreSQL
- `POST /api/v1/auth/login` validates credentials and returns a JWT
- `GET /api/v1/auth/me` returns the logged-in user's profile
- The BFF validates the JWT on every protected request by calling the Identity Service

---

## Component Map (what calls what)

```
curl / browser
   ↓  REST
BFF (Port 8000)              ← validates JWT
   ↓  REST  (internal)
Identity Service (Port 8001) ← owns passwords, issues JWTs
   ↓  SQL (asyncpg)
PostgreSQL identity.users    ← stores hashed passwords
```

---

## Proposed Changes

### Identity Service (`backend/services/identity/`)

#### [NEW] `database.py`
- SQLAlchemy async engine using `DATABASE_URL` from `.env`
- `AsyncSessionLocal` factory (used in FastAPI dependency injection)
- `get_db()` async generator — yields a session, closes after request

#### [NEW] `models.py`
- `User` ORM class inheriting from `shared.Base` + `TimestampMixin`
- Table: `identity.users` (uses `__table_args__ = {"schema": "identity"}`)
- Columns: `id` (UUID PK), `email` (unique), `display_name`, `password_hash`

#### [NEW] `schemas.py`
Pydantic request/response models (validation layer):
- `RegisterRequest` — email, display_name, password (min 8 chars)
- `LoginRequest` — email, password
- `TokenResponse` — access_token, refresh_token, token_type
- `UserResponse` — id, email, display_name, created_at

#### [NEW] `routers/__init__.py` + `routers/auth.py`
Three endpoints:
- `POST /auth/register` — hash password (Argon2) → insert User → return UserResponse
- `POST /auth/login` — verify password (Argon2) → create JWT pair → return TokenResponse
- `GET /auth/me` — decode JWT (passed as header by BFF) → return UserResponse

#### [MODIFY] `main.py`
- Mount: `app.include_router(auth_router, prefix="/auth", tags=["Auth"])`

#### [NEW] Alembic Setup
- `alembic.ini` — points to identity service's DB URL
- `alembic/env.py` — async-compatible env, imports `User` model so autogenerate works
- Run `alembic revision --autogenerate -m "create users table"`
- Run `alembic upgrade head` → creates `identity.users` in PostgreSQL

---

### BFF (`backend/bff/`)

#### [NEW] `dependencies.py`
- `get_current_user(token)` — FastAPI `Depends()` that:
  1. Extracts Bearer token from `Authorization` header
  2. Calls Identity Service's `GET /auth/me` with the token
  3. Returns user dict or raises HTTP 401

#### [NEW] `routers/__init__.py` + `routers/auth.py`
BFF auth proxy — forwards requests to Identity Service using `httpx`:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me` — uses `get_current_user` dependency

#### [MODIFY] `main.py`
- Mount `auth_router` at `/api/v1/auth`

---

## Verification Plan

### Setup commands (run once)
```powershell
# Identity Service venv
cd backend/services/identity
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ..\..\..\shared

# Run Alembic migration
alembic upgrade head

# Start identity service
uvicorn main:app --port 8001 --reload
```

```powershell
# BFF venv (new terminal)
cd backend/bff
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ..\..\shared

# Start BFF
uvicorn main:app --port 8000 --reload
```

### API Endpoint Tests (curl)
```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@hub.local","display_name":"Dev","password":"secret123"}'
# Expected: {"id":"...","email":"dev@hub.local","display_name":"Dev","created_at":"..."}

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@hub.local","password":"secret123"}'
# Expected: {"access_token":"eyJ...","refresh_token":"eyJ...","token_type":"bearer"}

# 3. Get profile (use access_token from step 2)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
# Expected: {"id":"...","email":"dev@hub.local",...}

# 4. Wrong password test
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@hub.local","password":"wrongpassword"}'
# Expected: HTTP 401 {"detail":"Invalid credentials"}
```

> [!NOTE]
> Virtual environments are per-service (`identity/.venv`, `bff/.venv`). 
> Each service runs in its own terminal with its own activated venv.
