# Phase 4: Automation Worker — Implementation Plan

This plan details the steps to implement the Automation Worker microservice, integrate it with the API Gateway (BFF), and build the Automation Hub UI in the Next.js frontend.

## User Review Required

> [!CAUTION]
> Safety Context: The Automation Worker will execute arbitrary shell commands using `subprocess`. Since this is a local, single-developer tool, this is acceptable. However, it's important to acknowledge that this service has full host-level access to execute scripts.

## Proposed Changes

---

### Backend: Automation Worker (Port 8003)

The internal microservice responsible for executing shell scripts and storing their execution history in PostgreSQL using the `automation` schema.

#### [NEW] `backend/services/automation_worker/alembic.ini` and `alembic/`
- Initialize Alembic for async migrations. Configure it to connect to the PostgreSQL database `DATABASE_URL`.

#### [NEW] `backend/services/automation_worker/database.py`
- Setup SQLAlchemy async engine and [get_db](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/identity/database.py#71-90) dependency. We will reuse the async PG URL from [.env](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/.env).

#### [NEW] `backend/services/automation_worker/models.py`
- Define `Execution` SQLAlchemy model mapping to `automation.executions` table.
- Columns: `id` (UUID), `script_content` (Text), `status` (String: Pending, Success, Failed), `exit_code` (Integer), `output` (Text), `created_at`, `updated_at`.

#### [NEW] `backend/services/automation_worker/schemas.py`
- Pydantic models: `ScriptRunRequest`, `ExecutionResponse`, `ExecutionListResponse`.

#### [NEW] `backend/services/automation_worker/routers/scripts.py`
- `POST /scripts/run`: Receives a script, creates a DB record (Pending), executes it via `asyncio.create_subprocess_shell`, captures output/exit code, and updates DB record.
- `GET /scripts/executions`: Returns a list of past executions, ordered by `created_at` DESC.
- `GET /scripts/executions/{id}`: Returns details of a specific execution.

#### [MODIFY] [backend/services/automation_worker/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/automation_worker/main.py)
- Include the `scripts` router.

---

### Backend: BFF API Gateway (Port 8000)

The API Gateway will expose the Automation Worker to the frontend and ensure authentication.

#### [NEW] `backend/bff/routers/scripts.py`
- Define proxy endpoints that forward requests from `/api/v1/scripts/*` to `http://localhost:8003/scripts/*`.
- Ensure JWT validation middleware/dependency is applied so only authenticated requests are forwarded.

#### [MODIFY] [backend/bff/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/main.py)
- Include the `scripts` router to expose the new endpoints.

---

### Frontend: Next.js Dashboard

The user interface to submit scripts and view past executions.

#### [NEW] `frontend/src/lib/api/automation.ts`
- Functions: `runScript(script: string)`, `getExecutions()`, `getExecution(id: string)` using the `fetch` API against the BFF `http://localhost:8000/api/v1/scripts`.

#### [NEW] `frontend/src/app/dashboard/automation/page.tsx`
- **UI Components**:
  - A split view or a primary list of past executions.
  - A "New Automation" button to open a modal/dialog.
  - The modal will contain a `textarea` for the bash/shell script and a "Run" button.
- **State**: Use React hooks to fetch executions and handle form submission.

#### [MODIFY] [frontend/src/app/dashboard/layout.tsx](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/app/dashboard/layout.tsx)
- Add "Automation Hub" to the Sidebar Navigation Menu.

---

## Verification Plan

### Automated / Backend Tests
We will verify the endpoints directly using `curl` or a Python script:
1. Ensure the PostgreSQL database is running via Docker Compose.
2. Run database migrations: `cd backend/services/automation_worker && alembic upgrade head`.
3. Start the internal service: `uvicorn main:app --port 8003`.
4. Send a test script: `curl -X POST http://localhost:8003/scripts/run -H "Content-Type: application/json" -d '{"script_content": "echo Hello World"}'`
5. Verify it returns `{ "output": "Hello World\n", "exit_code": 0, "status": "Success" }`.

### Manual Testing with Frontend
1. Start the BFF API Gateway (`uvicorn main:app --port 8000`).
2. Start the Next.js frontend (`npm run dev` in `frontend/`).
3. Open the browser to `localhost:3000/dashboard`, log in.
4. Navigate to the **Automation Hub**.
5. Click "New Automation", enter `pwd` and `echo "Testing 123"`, and click Run.
6. Verify the UI updates to show the execution result and output.
