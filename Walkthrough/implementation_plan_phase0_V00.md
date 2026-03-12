# Phase 0: Monorepo Setup & Infrastructure

## Goal
Establish the complete project skeleton: folder structure, Git, Docker Compose (PostgreSQL + MinIO), Python virtual environments, and the `shared/` package scaffold. After this phase, `docker compose up -d` will bring up all infrastructure services and the monorepo will be ready for active development.

---

> [!IMPORTANT]
> **No application code is written in this phase.** Phase 0 is purely infrastructure and scaffolding. The payoff is that every subsequent phase starts from a clean, consistent baseline.

---

## Proposed Changes

### Monorepo Root

#### [NEW] [docker-compose.yml](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/docker-compose.yml)
Spins up two infrastructure services:
- **PostgreSQL 16** on port `5432` with a persistent named volume (`pg_data`)
- **MinIO** on ports `9000` (API) and `9001` (browser console) with a persistent volume (`minio_data`)
- Both services use credentials from a `.env` file

#### [NEW] [.env](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/.env)
Environment variable file (gitignored). Contains DB credentials, MinIO credentials, JWT secret.

#### [NEW] [.gitignore](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/.gitignore)
Monorepo-level gitignore covering: `.env`, `node_modules/`, `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`

---

### Backend Scaffold

#### [NEW] `backend/shared/` Python Package
- `backend/shared/__init__.py`
- `backend/shared/auth/jwt_handler.py` — stub for JWT encode/decode (to be expanded in Phase 1)
- `backend/shared/logging/logger.py` — structured JSON logger using Python `logging` + `python-json-logger`
- `backend/shared/models/base.py` — SQLAlchemy `DeclarativeBase` shared across all services
- `backend/shared/pyproject.toml` — makes `shared` installable as a local pip package (`pip install -e ./backend/shared`)

#### [NEW] `backend/bff/` Skeleton
- `backend/bff/main.py` — FastAPI app with a single health-check endpoint `GET /health`
- `backend/bff/requirements.txt` — FastAPI, uvicorn, httpx (HTTP client for calling microservices)
- `backend/bff/.venv/` — isolated virtual environment (created during setup, gitignored)

#### [NEW] `backend/services/identity/` Skeleton
- `backend/services/identity/main.py` — FastAPI app with `GET /health`
- `backend/services/identity/requirements.txt`
- `backend/services/identity/alembic.ini` + `backend/services/identity/alembic/` — Alembic migration environment (empty, ready for Phase 1 schema)

#### [NEW] Skeleton `requirements.txt` for remaining services
- `snippet_engine/`, `automation_worker/`, `blob_service/`, `analytics/` — each gets a `main.py` (health check), `requirements.txt`, and empty Alembic setup

---

### Frontend Scaffold

#### [NEW] `frontend/` — Next.js 15 App
Bootstrapped using:
```
npx create-next-app@latest . --typescript --app --tailwind=false --eslint --src-dir --import-alias "@/*"
```
Then install MUI:
```
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
```

---

### Scripts

#### [NEW] `scripts/dev-start.ps1`
A PowerShell script that:
1. `docker compose up -d` — starts infra
2. Prints health check URLs for each service

---

## Verification Plan

### Automated Checks

**1. Docker Compose Health Check**
```powershell
# From Dev-Hub root:
docker compose up -d
docker compose ps
# Expected: postgres and minio show status "healthy" or "running"
```

**2. PostgreSQL Connectivity Check**
```powershell
docker exec -it devhub-postgres psql -U devhub_user -d devhub_db -c "\l"
# Expected: Lists databases including devhub_db
```

**3. MinIO Console Accessibility**
- Open browser: `http://localhost:9001`
- Login with credentials from `.env` (default: `minioadmin` / `minioadmin`)
- Expected: MinIO admin console loads

**4. BFF Health Check**
```powershell
# From backend/bff/ (with venv active):
uvicorn main:app --port 8000
curl http://localhost:8000/health
# Expected: {"status": "ok", "service": "bff"}
```

**5. shared/ Package Install Verification**
```powershell
# From backend/bff/ venv:
pip install -e ../../shared
python -c "from shared.logging.logger import get_logger; print('shared OK')"
# Expected: "shared OK" printed
```

**6. Next.js Dev Server**
```powershell
cd frontend
npm install
npm run dev
# Expected: Server starts on http://localhost:3000, no build errors
```

> [!NOTE]
> There are no existing tests in the repo yet (empty project). Verification at this stage is purely infrastructure health checks via CLI commands and browser access.
