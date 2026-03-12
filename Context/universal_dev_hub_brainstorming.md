# Brainstorming Session: Universal Dev-Hub
### Last Updated: 2026-03-12 | Status: LOCKED FOR MVP

---

## 1. Problem Statement & Motivation
As an intermediate C++ developer transitioning to web development, learning a modern full-stack ecosystem (Next.js, Python FastAPI, PostgreSQL, Microservices) can be overwhelming if done without a focused, realistic project.

The **Universal Dev-Hub** solves two problems simultaneously:
1. Provides a highly relevant, real-world development environment to learn advanced architectural patterns (BFF, gRPC, MinIO, Docker Compose, Alembic, JWT auth).
2. Yields a genuinely useful local productivity tool that enhances daily development tasks.

---

## 2. Target Audience & Constraints
- **Primary User**: Single developer (single-tenant).
- **Environment**: 100% Local (Windows laptop). No cloud dependencies.
- **Goal**: Master production-grade practices (auth, validation, inter-service communication over REST/gRPC, blob storage, DB migrations).

---

## 3. Core Feature Brainstorming

| Feature | Description | Why? |
|---|---|---|
| **Auth** | Username/password login with JWT | Learn industry-standard stateless auth (GitHub SSO deferred to V2) |
| **Snippets** | Store, tag, and search C++, Python, or Bash snippets | Core use case; the gRPC learning component |
| **Files** | Upload architecture diagrams, PDFs, demo videos to MinIO | Learn S3-compatible blob storage |
| **Automation** | Execute heavy C++ compilation scripts or Python data tasks via a button | Learn subprocess management + REST |
| **Analytics** | "How many snippets? How many scripts ran?" Dashboard charts | Learn time-series aggregation + chart visualisation |

---

## 4. Architectural Paradigms (The "Why")

| Decision | Rationale |
|---|---|
| **Next.js 15 + MUI 7** | Production-grade routing (`app/`) and UI components; mirrors industry standards |
| **BFF (Backend for Frontend)** | Standard pattern to decouple the UI from backend service orchestration; single gateway |
| **gRPC for Snippets** | Binary-efficient; Protobuf schema resembles C++ struct definitions — a natural bridge |
| **MinIO** | S3-compatible blob storage on localhost — zero cloud cost, production-identical API |
| **Docker Compose** | Industry standard for local infra management; eliminates manual Postgres/MinIO install pain |
| **Alembic Migrations** | Version-controlled schema changes — treat DB like code; prevents manual mistakes |
| **JWT (not sessions)** | Stateless auth; scales across multiple services without shared session storage |
| **`shared/` Python package** | Eliminates code duplication across 6 services; monorepo best practice |

---

## 5. Scope Management (MVP vs V2)

### MVP (In Scope — Currently Building)
- ✅ Username/password registration + JWT auth
- ✅ Basic CRUD operations for Snippets via gRPC
- ✅ Triggering a Python script via Automation Worker (subprocess)
- ✅ Uploading a file to MinIO via Blob Service
- ✅ Dashboard analytics with live charts
- ✅ Docker Compose infrastructure (Postgres + MinIO)
- ✅ Alembic migrations for all services
- ✅ Shared Python package for common logic

### V2 (Deferred — Future Learning)
- 🔜 GitHub OAuth SSO (PKCE flow)
- 🔜 Real-time WebSockets for streaming subprocess stdout
- 🔜 IndexedDB offline-first snippet sync (stale-while-revalidate)
- 🔜 Cross-service correlation IDs in structured logs (already architected, implementation deferred)

---

## 6. Learning Milestones

| Phase | Key Learning |
|---|---|
| Phase 0 | Docker, docker-compose, .env files, local infra management |
| Phase 1 | FastAPI, Pydantic, Argon2, JWT, REST API design, Alembic |
| Phase 2 | Next.js App Router, React hooks, MUI components, TypeScript |
| Phase 3 | Protocol Buffers, gRPC server/client in Python, serialization |
| Phase 4 | Python subprocess, OS process management, async patterns |
| Phase 5 | MinIO SDK, multipart uploads, pre-signed URLs |
| Phase 6 | Time-series data, aggregation queries, ApexCharts |
| Phase 7 | IndexedDB, service workers, offline-first patterns |
