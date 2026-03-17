# Phase 3: Snippet Engine (gRPC + Protobufs)

## Goal
By the end of this phase:
- [protos/snippet.proto](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto) defines the gRPC contract for snippet CRUD
- Snippet Engine runs a gRPC server on port 8002
- BFF proxies REST → gRPC (the frontend never touches gRPC directly)
- Snippet Library UI page: create, view, edit, and delete code snippets

---

## What is gRPC? (Quick Mental Model)

> **REST** = HTTP + JSON → human-readable, flexible, widely understood
> **gRPC** = HTTP/2 + Protobuf → binary, typed, auto-generates client/server code
>
> Think of [.proto](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto) files as **C++ header files** — they define the interface.
> `grpcio-tools` compiles them into Python classes (like compiling `.h` → `.o`).
>
> The BFF speaks REST to the browser, then translates to gRPC for the Snippet Engine.

---

## Proposed Changes

### 1. Proto Definition

#### [MODIFY] [protos/snippet.proto](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto)
Define the gRPC service contract:
- **Messages**: [Snippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#32-33), `CreateSnippetRequest`, `SnippetFilter`, [SnippetList](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#73-77), [SnippetId](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#49-52), [Empty](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#78-79)
- **Service [SnippetService](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#30-36)**: 5 RPCs:
  - [CreateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#31-32) → creates and returns the snippet
  - [GetSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#32-33) → get one by ID
  - `ListSnippets` → list all for a user (with optional language/tag filter)
  - `UpdateSnippet` → update title/code/language/tags
  - [DeleteSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#34-35) → delete by ID

#### [NEW] `backend/services/snippet_engine/generated/` — auto-generated Python stubs
Run: `python -m grpc_tools.protoc --python_out=./generated --grpc_python_out=./generated -I../../protos ../../protos/snippet.proto`

---

### 2. Snippet Engine Service (Port 8002)

#### [NEW] `snippet_engine/database.py`
Async SQLAlchemy engine + [get_db()](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/identity/database.py#71-90) session factory (same pattern as Identity Service)

#### [NEW] `snippet_engine/models.py`
[Snippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#32-33) ORM model → `snippets.snippets` table:
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK, auto-generated |
| user_id | UUID | NOT NULL (owner) |
| title | VARCHAR(200) | NOT NULL |
| language | VARCHAR(50) | NOT NULL |
| code | TEXT | NOT NULL |
| tags | ARRAY(String) | Optional array of tag strings |
| created_at | TIMESTAMP(tz) | auto via TimestampMixin |
| updated_at | TIMESTAMP(tz) | auto via TimestampMixin |

#### [NEW] `snippet_engine/alembic/` — Alembic setup (same pattern as Identity)
Migration to create `snippets.snippets` table using psycopg2 sync driver.

#### [MODIFY] [snippet_engine/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/snippet_engine/main.py)
gRPC async server: implements `SnippetServiceServicer` with all 5 RPCs.

---

### 3. BFF — gRPC Client Proxy

#### [NEW] `backend/bff/routers/snippets.py`
5 REST endpoints that translate to gRPC calls:
| REST Endpoint | gRPC Call |
|---|---|
| `POST /api/v1/snippets` | [CreateSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#31-32) |
| `GET /api/v1/snippets/:id` | [GetSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#32-33) |
| `GET /api/v1/snippets` | `ListSnippets` (query params: language, tag) |
| `PUT /api/v1/snippets/:id` | `UpdateSnippet` |
| `DELETE /api/v1/snippets/:id` | [DeleteSnippet](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto#34-35) |

All protected by [get_current_user](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py#30-54) cookie dependency.

#### [MODIFY] [backend/bff/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/main.py)
Mount snippets router at `/api/v1/snippets`.

---

### 4. Frontend — Snippet Library UI

#### [NEW] `frontend/src/app/dashboard/snippets/page.tsx`
- **Top section**: "Create Snippet" button → opens dialog/drawer
- **Grid of snippet cards**: title, language badge, first 3 lines of code preview, tags
- **Search bar** + **language filter** dropdown
- **Click card** → opens detail view with full code + edit/delete buttons

#### [NEW] `frontend/src/components/SnippetDialog.tsx`
- Modal dialog for creating/editing snippets
- Fields: title, language dropdown, code textarea, tags input
- Submit calls BFF → gRPC → DB

#### Enable sidebar "Snippets" link (remove `disabled: true`)

---

## Verification Plan

### Automated Tests
1. Compile [.proto](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/protos/snippet.proto) → generates `snippet_pb2.py` + `snippet_pb2_grpc.py`
2. `alembic upgrade head` → creates `snippets.snippets` table
3. gRPC server starts on port 8002
4. BFF curl tests: create snippet, list, get by ID, update, delete
5. Frontend: create a snippet, see it in the list, edit it, delete it

### Commands
```bash
# Start snippet engine
cd backend/services/snippet_engine
.venv\Scripts\python.exe main.py

# Test via BFF
curl -b cookies.txt POST /api/v1/snippets -d '{"title":"Hello","language":"python","code":"print(42)"}'
curl -b cookies.txt GET  /api/v1/snippets
```
