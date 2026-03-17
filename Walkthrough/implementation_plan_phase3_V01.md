# Phase 3: Snippet Engine (gRPC + Protobufs) — Implementation Plan

## Goal

Implement the full Snippet Engine service with gRPC CRUD operations, BFF REST→gRPC proxy, and a Snippet Library UI page in the Next.js frontend. Uses PostgreSQL running in Docker (port 5433, schema `snippets`).

---

## Proposed Changes

### 1. Snippet Engine Backend (gRPC Service on port 8002)

#### [NEW] `backend/services/snippet_engine/database.py`
- Async SQLAlchemy engine + [get_db()](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/identity/database.py#71-90) session factory (mirrors Identity Service pattern)
- Reads `DATABASE_URL` from [.env](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/.env) via `dotenv`

#### [NEW] `backend/services/snippet_engine/models.py`
- [Snippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#34-44) ORM model → `snippets.snippets` table:
  - [id](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/shared/devhub_shared/models/base.py#72-75) (UUID PK), `user_id` (UUID, NOT NULL), `title` (VARCHAR 200), `language` (VARCHAR 50), `code` (TEXT), `tags` (ARRAY of String), `created_at`, `updated_at` via TimestampMixin

#### [NEW] `backend/services/snippet_engine/alembic.ini`
- Config pointing to `alembic/` directory, same pattern as Identity Service

#### [NEW] `backend/services/snippet_engine/alembic/env.py`
- Imports [Snippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#34-44) model, uses psycopg2 sync driver for migrations
- `version_table_schema="snippets"` (keeps Alembic version tracking in the snippets schema)

#### [NEW] `backend/services/snippet_engine/alembic/script.py.mako`
- Same template as Identity Service

#### [NEW] `backend/services/snippet_engine/alembic/versions/` (auto-generated)
- Migration to create `snippets.snippets` table

#### [NEW] `backend/services/snippet_engine/generated/` (auto-generated gRPC stubs)
- `snippet_pb2.py` + `snippet_pb2_grpc.py` generated from [protos/snippet.proto](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto)

#### [MODIFY] [backend/services/snippet_engine/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/snippet_engine/main.py)
- Replace placeholder with full async gRPC server implementing `SnippetServiceServicer`:
  - [CreateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#91-93), [GetSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#94-96), [ListSnippets](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#97-99), [UpdateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#100-102), [DeleteSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#103-105)
- Uses async SQLAlchemy sessions for DB operations

#### [MODIFY] [backend/services/snippet_engine/requirements.txt](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/snippet_engine/requirements.txt)
- Add `psycopg2-binary` for Alembic sync migrations

---

### 2. BFF — gRPC Client Proxy

#### [NEW] `backend/bff/routers/snippets.py`
- 5 REST endpoints translating to gRPC calls via `grpcio`:
  - `POST /api/v1/snippets` → [CreateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#91-93)
  - `GET /api/v1/snippets/{id}` → [GetSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#94-96)
  - `GET /api/v1/snippets` → [ListSnippets](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#97-99) (query params: language, tag, search)
  - `PUT /api/v1/snippets/{id}` → [UpdateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#100-102)
  - `DELETE /api/v1/snippets/{id}` → [DeleteSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#103-105)
- All protected by [get_current_user](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py#30-54) cookie dependency
- Uses gRPC channel to `localhost:8002`

#### [MODIFY] [backend/bff/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/main.py)
- Mount snippets router: `app.include_router(snippets_router, prefix="/api/v1/snippets", tags=["Snippets"])`

#### [MODIFY] [backend/bff/requirements.txt](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/requirements.txt)
- Add `grpcio` and `protobuf` dependencies

#### [NEW] `backend/bff/generated/` (copy of the generated gRPC stubs)
- BFF needs the same `snippet_pb2.py` + `snippet_pb2_grpc.py` to create gRPC client stubs

---

### 3. Frontend — Snippet Library UI

#### [NEW] `frontend/src/app/dashboard/snippets/page.tsx`
- **Top section**: "Create Snippet" button + search bar + language filter dropdown
- **Grid of snippet cards**: title, language badge, code preview (first 3 lines), tags
- **Click card** → inline expand or detail modal with full code + edit/delete buttons
- Uses established theme: Deep Navy + Cyan accent, glassmorphism cards

#### [NEW] `frontend/src/components/SnippetDialog.tsx`
- Modal dialog for creating/editing snippets
- Fields: title, language dropdown, code textarea (monospaced), tags input (chip-style)
- Submit calls BFF API

#### [MODIFY] [frontend/src/app/dashboard/layout.tsx](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/app/dashboard/layout.tsx)
- Remove `disabled: true` from the "Snippets" nav item in `NAV_ITEMS` array

---

## Verification Plan

### Automated Tests (curl via terminal)

1. **Proto compilation**: Generate stubs and verify files exist
2. **Alembic migration**: `alembic upgrade head` creates `snippets.snippets` table
3. **gRPC server starts**: `python main.py` runs on port 8002 without errors
4. **BFF curl tests** (all require login cookie):
   ```powershell
   # Login first
   curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"dev@example.com","password":"..."}'
   
   # Create snippet
   curl -b cookies.txt -X POST http://localhost:8000/api/v1/snippets -H "Content-Type: application/json" -d '{"title":"Hello World","language":"python","code":"print(42)","tags":["test"]}'
   
   # List snippets
   curl -b cookies.txt http://localhost:8000/api/v1/snippets
   
   # Get by ID
   curl -b cookies.txt http://localhost:8000/api/v1/snippets/{id}
   
   # Update
   curl -b cookies.txt -X PUT http://localhost:8000/api/v1/snippets/{id} -H "Content-Type: application/json" -d '{"title":"Updated","language":"python","code":"print(99)","tags":["updated"]}'
   
   # Delete
   curl -b cookies.txt -X DELETE http://localhost:8000/api/v1/snippets/{id}
   ```

### Browser Verification
5. **Frontend**: Navigate to `http://localhost:3000/dashboard/snippets`, create a snippet, see it in the grid, edit it, delete it — verify sidebar link is active (no "Soon" badge)
