# Product Requirements Document (PRD): Universal Dev-Hub
### Last Updated: 2026-03-12 | Status: APPROVED — Phase 0 Starting

---

## 1. Executive Summary
The **Universal Dev-Hub** is a locally hosted, 6-service microservice ecosystem (1 BFF + 5 microservices) designed to centralize developer productivity. It provides identity management, high-performance code snippet storage, local automation execution, binary file management, and system analytics — all driven by a Next.js frontend mimicking modern cloud platforms. It is built as a **learn-by-doing project** for an intermediate C++ developer transitioning to web development.

---

## 2. Goals & Non-Goals

### 2.1 Goals (MVP)
- Build a 100% locally-run microservices architecture orchestrated via Docker Compose.
- Implement secure authentication using **username/password JWTs** (industry standard, no external OAuth dependency).
- Utilize both REST/JSON and gRPC for inter-service communication.
- Store structured data in PostgreSQL 16 and unstructured binary data in MinIO.
- Manage database schema evolution with **Alembic** (migration-first approach).
- Build a premium MUI 7-based Next.js 15 dashboard.
- Implement a `backend/shared/` Python package to eliminate code duplication across services.

### 2.2 Non-Goals (MVP)
- GitHub/Google OAuth SSO — deferred to **V2**.
- Cloud deployment or Kubernetes — out of scope.
- Multi-tenant RBAC — single developer focus.
- IndexedDB offline sync — deferred to **V2**.

---

## 3. User Stories

| # | Story | Service |
|---|---|---|
| US-01 | As a developer, I want to register and log in with username/password so I can access the hub securely. | Identity |
| US-02 | As a developer, I want to save a 500-line C++ snippet and retrieve it instantly so I can paste it into my IDE. | Snippet Engine |
| US-03 | As a developer, I want to upload an architecture diagram (PNG) to local blob storage so I can reference it. | Blob Service |
| US-04 | As a developer, I want to click "Run Build" to execute a local shell script and see its exit code. | Automation Worker |
| US-05 | As a developer, I want my dashboard to show daily usage charts so I can track productivity. | Analytics |

---

## 4. Functional Requirements

### 4.1 Frontend (Next.js 15 Dashboard)
- **Framework**: Next.js 15 (App Router), React 19, Material UI v7, TypeScript 5
- **Pages**: Login, Overview Dashboard, Snippet Library, File Manager, Automation Hub
- **Auth**: JWT stored in secure httpOnly cookies via BFF proxy
- **V2 Feature**: IndexedDB offline cache (stale-while-revalidate)

### 4.2 BFF — API Gateway (FastAPI, Port 8000)
- Single entry point for all frontend traffic
- Validates JWT on every request (calls Identity Service)
- Routes requests to downstream microservices using REST or gRPC
- Serializes gRPC responses to JSON before returning to frontend

### 4.3 Microservices

| # | Service | Port | Protocol | Database |
|---|---|---|---|---|
| 1 | Identity Service | 8001 | REST | PostgreSQL (users) |
| 2 | Snippet Engine | 8002 | gRPC | PostgreSQL (snippets) |
| 3 | Automation Worker | 8003 | REST | PostgreSQL (executions) |
| 4 | Blob Storage Service | 8004 | REST | PostgreSQL (files) + MinIO |
| 5 | Analytics Service | 8005 | REST | PostgreSQL (events agg.) |

#### Identity Service (8001)
- `POST /auth/register` — Create user with hashed password (Argon2)
- `POST /auth/login` — Validate credentials, return JWT (access + refresh tokens)
- `GET /auth/me` — Return current user profile (from JWT)
- **V2**: `GET /auth/github` — GitHub OAuth callback

#### Snippet Engine (8002 — gRPC)
- `rpc CreateSnippet (SnippetRequest) returns (SnippetResponse)`
- `rpc GetSnippets (SearchRequest) returns (SnippetListResponse)`
- `rpc GetSnippet (SnippetIdRequest) returns (SnippetResponse)`
- `rpc DeleteSnippet (SnippetIdRequest) returns (Empty)`

#### Automation Worker (8003)
- `POST /scripts/run` — Execute a shell script via Python `subprocess`
- `GET /scripts/executions` — List past execution records
- `GET /scripts/executions/{id}` — Get single execution detail

#### Blob Storage Service (8004)
- `POST /files/upload` — Upload a file (multipart); store binary in MinIO, metadata in PG
- `GET /files` — List all files for the current user
- `GET /files/{id}/download` — Generate pre-signed MinIO URL for download
- `DELETE /files/{id}` — Remove file from MinIO and PG

#### Analytics Service (8005)
- `POST /events` — Ingest an event (called internally by BFF after actions)
- `GET /analytics/summary` — Return dashboard summary metrics
- `GET /analytics/executions/daily` — Return 30-day execution time series

---

## 5. Security & Authentication
- Frontend sends `Authorization: Bearer <JWT>` to BFF
- BFF validates JWT on **every request** before routing to internal services
- Internal services trust the BFF and do not re-validate JWTs (internal network trust)
- Passwords hashed with **Argon2** (not bcrypt — Argon2 is the OWASP-recommended standard)
- JWT secret stored in `.env` file (gitignored)

---

## 6. Non-Functional Requirements
- **Infra**: All infrastructure (Postgres + MinIO) spun up via `docker compose up -d`
- **Migrations**: All DB changes managed via Alembic — no direct schema modifications
- **Logging**: Structured JSON logs with `correlation_id` on every request across all services
- **Code Reuse**: `backend/shared/` package shared across BFF and all 5 microservices
