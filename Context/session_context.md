# Full-Stack Architectural Context: Universal Dev-Hub

## I. Core Tech Stack (Confirmed & Locked)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI Engine**: React 19
- **Design System**: Material UI (MUI) 7 + Emotion (CSS-in-JS)
- **Type Safety**: TypeScript 5
- **Form/Schema**: React Hook Form + Zod (Runtime validation)
- **Date Handling**: Day.js

### Backend
- **Language**: Python 3.14.3
- **Framework**: FastAPI (for BFF and all microservices)
- **ORM**: SQLAlchemy 2.x (async)
- **DB Migrations**: **Alembic** (one migration environment per service)
- **Auth**: JWT (access + refresh tokens via `python-jose`); password hashing via `argon2-cffi`

### Infrastructure (Local)
- **Database**: PostgreSQL 16 (via Docker)
- **Object Storage**: MinIO (via Docker, S3-compatible API)
- **Containerization**: Docker Desktop 29.0.1 + `docker-compose.yml` (single file spins entire infra)

### Runtime Versions (Confirmed)
- Docker: 29.0.1
- Node.js: v24.13.1
- Python: 3.14.3

---

## II. Architectural & Design Patterns

### Accepted Architectural Decisions (ADRs)

| ID | Decision | Rationale |
|---|---|---|
| ADR-001 | BFF Pattern (FastAPI Gateway at Port 8000) | Decouples UI from internal service topology |
| ADR-002 | gRPC for Snippet Engine (Port 8002) | High-throughput binary payloads; learning bridge to C++ structs |
| ADR-003 | **Username/Password JWT for MVP Auth** (not OAuth SSO) | Removes external dependency (GitHub/Google app registration). GitHub SSO deferred to V2. |
| ADR-004 | Docker Compose for ALL infrastructure from Day 1 | Production-grade local dev; single command spin-up |
| ADR-005 | Alembic for DB Migrations across all services | Version-controlled schema changes; industry standard |
| ADR-006 | `backend/shared/` Python package | Avoid code duplication across 6 services (JWT validation, logging config, base models) |
| ADR-007 | Structured JSON Logging + Correlation IDs | Traceable requests across microservice chain |
| ADR-008 | IndexedDB Offline-First Cache (V2) | Stale-while-revalidate strategy via background worker |

### Communication Protocols
- **Frontend → BFF**: REST/JSON over HTTP
- **BFF → Identity, Automation, Blob, Analytics**: REST/JSON (inter-process HTTP)
- **BFF → Snippet Engine**: gRPC (Protocol Buffers)
- **Auth**: `Authorization: Bearer <JWT>` on all BFF requests; BFF validates with Identity Service

---

## III. Project Structure (Monorepo)

```
Dev-Hub/
├── Context/                        # Project documentation
├── docker-compose.yml              # PostgreSQL 16 + MinIO (infra only)
├── .env                            # Shared secrets (gitignored)
├── .gitignore
├── frontend/                       # Next.js app
│   ├── src/
│   │   ├── app/                   # App Router pages
│   │   ├── components/            # MUI UI atoms
│   │   ├── hooks/                 # Shared business logic
│   │   ├── lib/                   # API client, IDB cache
│   │   └── contexts/              # React global state
│   └── package.json
├── backend/
│   ├── shared/                    # Common Python package
│   │   ├── auth/                  # JWT encode/decode helpers
│   │   ├── logging/               # Structured JSON logger
│   │   └── models/                # Shared Pydantic base models
│   ├── bff/                       # API Gateway (Port 8000)
│   └── services/
│       ├── identity/              # Auth service (Port 8001)
│       ├── snippet_engine/        # gRPC service (Port 8002)
│       ├── automation_worker/     # Process runner (Port 8003)
│       ├── blob_service/          # MinIO wrapper (Port 8004)
│       └── analytics/             # Metrics service (Port 8005)
├── protos/                        # Shared .proto definitions
└── scripts/                       # Dev helper scripts
```

---

## IV. Service Port Map

| Service | Port | Protocol | DB |
|---|---|---|---|
| BFF (API Gateway) | 8000 | REST | — |
| Identity Service | 8001 | REST | PostgreSQL (users) |
| Snippet Engine | 8002 | gRPC | PostgreSQL (snippets) |
| Automation Worker | 8003 | REST | PostgreSQL (executions) |
| Blob Storage Service | 8004 | REST | PostgreSQL (files) + MinIO |
| Analytics Service | 8005 | REST | PostgreSQL (events) |
| PostgreSQL | 5432 | SQL | — |
| MinIO API | 9000 | S3 API | — |
| MinIO Console | 9001 | HTTP | — |

---

## V. User Profile & Learning Goals
- **Profile**: Intermediate C++ Developer (transitioning to Web Architect)
- **Primary Goals**: Master Next.js/React, Auth Workflows, Microservices (REST/gRPC), Alembic, Docker, Offline-First State
- **Environment**: 100% Local (Docker-managed Postgres + MinIO, Python, Node.js)
- **Learning Phases**: Phase 0 (Infra) → Phase 1 (Auth) → Phase 2 (Frontend) → Phase 3 (gRPC) → Phase 4-6 (Workers) → Phase 7-8 (V2)
