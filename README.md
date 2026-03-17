# Universal Dev-Hub

Welcome to Universal Dev-Hub! This guide will help you start all the necessary services after restarting your computer.

Because this project uses a microservices architecture, there are several components that need to be started for the application to function fully.

## Prerequisites
Ensure Docker Desktop is running before starting the services.

---

## Startup Instructions

### Quick Start (Recommended for Windows)
We have provided an automated PowerShell script that spins up the entire infrastructure (Docker, all 5 Python Microservices, API Gateway, and Next.js Frontend) in separate terminal windows automatically.

Open a PowerShell terminal as Administrator (or ensure execution policies allow scripts) in the root directory:
```powershell
.\start_all.ps1
```

If you prefer to start them manually, follow the steps below.

---

### Manual Startup

### 1. Start the Database (Docker)
Open a terminal in the root `Dev-Hub` directory.
```powershell
docker compose up -d
```
*(This starts PostgreSQL on port 5432 and MinIO)*

### 2. Start the Identity Service (Port 8001)
Open a new terminal.
```powershell
cd backend\services\identity
.\.venv\Scripts\activate
uvicorn main:app --port 8001 --reload
```

### 3. Start the Snippet Engine (Port 8002)
Open a new terminal.
```powershell
cd backend\services\snippet_engine
.\.venv\Scripts\activate
uvicorn main:app --port 8002 --reload
```

### 4. Start the Automation Worker (Port 8003)
Open a new terminal.
```powershell
cd backend\services\automation_worker
.\.venv\Scripts\activate
uvicorn main:app --port 8003 --reload
```

### 5. Start the Blob Storage Service (Port 8004)
Open a new terminal.
```powershell
cd backend\services\blob_service
.\.venv\Scripts\activate
uvicorn main:app --port 8004 --reload
```

### 6. Start the Analytics Service (Port 8005)
Open a new terminal.
```powershell
cd backend\services\analytics
.\.venv\Scripts\activate
uvicorn main:app --port 8005 --reload
```

### 7. Start the API Gateway / BFF (Port 8000)
Open a new terminal.
```powershell
cd backend\bff
.\.venv\Scripts\activate
uvicorn main:app --port 8000 --reload
```

### 8. Start the Next.js Frontend (Port 3000)
Open a new terminal.
```powershell
cd frontend
npm run dev
```

---

## Access the Application
Once all services are running, open your web browser and navigate to:
**http://localhost:3000**

You can log in with your account or use the Sign Up option on the login page.

---

## Setting Up the Project for a New Developer

If you are a new developer cloning this repository for the first time, follow these steps to bootstrap your local environment.

### 1. Install Prerequisites
Ensure you have the following installed:
- **Docker Desktop** (for PostgreSQL and MinIO)
- **Node.js 20+** (for the Next.js frontend)
- **Python 3.12+** (for the backend microservices)
- **Rust Compiler** (needed to build `pydantic-core` and `asyncpg` on Windows). You can install it via [rustup.rs](https://rustup.rs/).

### 2. Set Up Environment Variables
Create a `.env` file in the root `Dev-Hub` directory. Ask a team member for the required values, or use standard local development defaults for `DATABASE_URL`, `JWT_SECRET_KEY`, etc.

### 3. Start Infrastructure
Run `docker compose up -d` in the root directory to start the database container.

### 4. Bootstrap Python Microservices
For **each** of the backend directories (`backend/bff`, `backend/services/identity`, `backend/services/snippet_engine`, `backend/services/automation_worker`, `backend/services/blob_service`, `backend/services/analytics`), run the following commands to create isolated virtual environments and install dependencies:

```powershell
# Run this inside each backend directory
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run Database Migrations (Critical!)
Before starting the services, you **must** apply the Alembic database migrations to create the required tables in PostgreSQL. See the "Understanding and Running Alembic Migrations" section below.

### 6. Start the Frontend
In the `frontend` directory, install Node dependencies:
```powershell
npm install
```

---

## Understanding and Running Alembic Migrations

**What is Alembic?**
Alembic is a database migration tool for SQLAlchemy. As we develop the application, we frequently change our database structure (adding new tables, new columns, etc.). Instead of manually running SQL scripts, Alembic reads Python-based "migration scripts" that define the exact steps (Upgrades) to apply those structural changes to the database. It guarantees that our database schema is version-controlled and consistent across all environments.

Each backend microservice has its own isolated database schema (e.g., `identity` schema, `automation` schema) and its own Alembic configuration.

### Common Issue: Missing Tables
If you ever wipe your Docker containers data (e.g., by running `docker compose down -v`), your PostgreSQL database will return to a completely empty state. **You must re-run all Alembic migrations** to recreate the tables before the app will work.

### How to Ensure All Alembic Steps Are Done

Whenever you pull new code or reset your database, you must run the migrations for **each backend microservice** that connects to the database.

**To run all migrations and bring your database fully up-to-date:**
Run these commands in order (assuming your Docker database is running):

**1. Identity Service Migrations:**
```powershell
cd backend/services/identity
.\.venv\Scripts\activate
alembic upgrade head
```

**2. Snippet Engine Migrations:**
```powershell
cd ../snippet_engine
.\.venv\Scripts\activate
alembic upgrade head
```

**3. Automation Worker Migrations:**
```powershell
cd ../automation_worker
.\.venv\Scripts\activate
alembic upgrade head
```

**4. Blob Storage Service Migrations:**
```powershell
cd ../blob_service
.\.venv\Scripts\activate
alembic upgrade head
```

**5. Analytics Service Migrations:**
```powershell
cd ../analytics
.\.venv\Scripts\activate
alembic upgrade head
```

The `alembic upgrade head` command tells Alembic to look at its internal tracking table in the database and automatically run every missing migration script until it reaches the latest version ("head").

### Useful Alembic Commands
Run these commands from inside a specific service directory (with its `.venv` activated):

- **Apply all pending migrations:**
  ```powershell
  alembic upgrade head
  ```

- **Downgrade/revert the last migration (if you make a mistake):**
  ```powershell
  alembic downgrade -1
  ```

- **Create a new migration script:** (Use this when you modify `models.py`)
  ```powershell
  alembic revision --autogenerate -m "added new feature table"
  ```
  *(Always double-check the generated file inside `alembic/versions/` to ensure it looks correct before running `upgrade head`!)*

- **Check current migration status:**
  ```powershell
  alembic current
  ```

---

## Troubleshooting
- **Identity Service is unavailable**: Ensure the Identity Service (Step 2 of Startup Instructions) is running.
- **Database Connection Errors**: Ensure Docker Desktop is running and you executed `docker compose up -d`.
- **ModuleNotFoundError**: Ensure you have activated the virtual environment (`.\.venv\Scripts\activate`) before running `uvicorn` or `alembic`.
- ** relation "identity.users" does not exist **: You forgot to run `alembic upgrade head` in the Identity service.
