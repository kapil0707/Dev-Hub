# Universal Dev-Hub — Project Task Tracker

## Phase 0: Monorepo Setup & Infrastructure
- [x] Update context documents with accepted architectural decisions
- [x] Create [docker-compose.yml](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/docker-compose.yml) (PostgreSQL 16 + MinIO)
- [x] Create monorepo folder skeleton (`frontend/`, `backend/`, `scripts/`, `protos/`)
- [x] Create `backend/shared/` Python package scaffold
- [x] Set up Python virtual environments per service
- [x] Verify `docker compose up` works and services are healthy
- [x] Initialize Git repo with `.gitignore`

## Phase 1: Identity Service + BFF Skeleton
- [ ] Create `backend/services/identity/` FastAPI project
- [ ] Implement username/password auth with Argon2 hashing
- [ ] Implement JWT issuance (access + refresh tokens)
- [ ] Set up Alembic migrations for `users` table
- [ ] Create `backend/bff/` FastAPI gateway skeleton
- [ ] Implement JWT validation middleware in BFF
- [ ] Wire BFF → Identity Service (REST)
- [ ] Test auth flow end-to-end with curl/Postman

## Phase 2: Next.js Frontend (Login + Dashboard Skeleton)
- [ ] Bootstrap Next.js 15 app with TypeScript + MUI 7
- [ ] Implement login page (username/password form)
- [ ] Implement JWT storage in httpOnly cookies (via BFF)
- [ ] Create dashboard shell layout (sidebar, topbar)
- [ ] Create 4 summary metric cards (Overview page)
- [ ] Set up client-side route guards (redirect to login if no token)

## Phase 3: Snippet Engine (gRPC + Protobufs)
- [ ] Define `protos/snippet.proto` schema
- [ ] Create `backend/services/snippet_engine/` FastAPI + gRPC server
- [ ] Set up Alembic migrations for `snippets` table
- [ ] Implement gRPC CRUD (CreateSnippet, GetSnippets, DeleteSnippet)
- [ ] Implement BFF → Snippet Engine gRPC client
- [ ] Build Snippet Library UI page in Next.js

## Phase 4: Automation Worker
- [ ] Create `backend/services/automation_worker/` FastAPI project
- [ ] Implement script execution via Python `subprocess`
- [ ] Set up Alembic migrations for `executions` table
- [ ] Create Automation Hub UI page in Next.js

## Phase 5: Blob Storage Service
- [ ] Create `backend/services/blob_service/` FastAPI project
- [ ] Integrate MinIO Python SDK for file upload/download
- [ ] Set up Alembic migrations for `files` table
- [ ] Create File Manager UI page in Next.js

## Phase 6: Analytics Service + Dashboard Charts
- [ ] Create `backend/services/analytics/` FastAPI project
- [ ] Implement event ingestion endpoint
- [ ] Implement aggregation queries
- [ ] Wire live data to the dashboard Overview charts

## Phase 7 (V2): IndexedDB Offline Sync
- [ ] Implement IndexedDB cache layer in `frontend/src/lib/`
- [ ] Implement background sync worker (stale-while-revalidate)
- [ ] Test offline behavior

## Phase 8 (V2): GitHub SSO
- [ ] Register OAuth2 app on GitHub
- [ ] Implement OAuth2 callback in Identity Service
- [ ] Update BFF to support SSO token flow
