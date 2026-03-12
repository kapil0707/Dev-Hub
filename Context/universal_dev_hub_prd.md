# Product Requirements Document (PRD): Universal Dev-Hub

## 1. Executive Summary
The **Universal Dev-Hub** is a locally hosted, 5-service microservice ecosystem designed to centralize developer productivity. It provides identity management, high-performance code snippet storage, local automation execution, binary file management, and system analytics, all driven by a Next.js frontend mimicking modern cloud platforms.

## 2. Goals & Non-Goals
### 2.1 Goals
- Build a 100% locally-run microservices architecture.
- Implement Single Sign-On (SSO) using Google/GitHub via an Identity Service.
- Utilize both REST/JSON and gRPC for inter-service communication.
- Store structured data in PostgreSQL and unstructured binary data in MinIO.
- Build a premium MUI-based Next.js dashboard.

### 2.2 Non-Goals
- Cloud deployment or container orchestration (Kubernetes) is out of scope for the MVP.
- Multi-tenant enterprise RBAC (Role-Based Access Control) is out of scope (single developer focus).

## 3. User Stories
- **As a developer**, I want to log in using my GitHub account so I don't have to manage local passwords.
- **As a developer**, I want to save a 500-line C++ snippet and retrieve it instantly via gRPC to paste into my IDE.
- **As a developer**, I want to upload an architecture diagram (PNG) to local blob storage so I can link it in my notes.
- **As a developer**, I want to click a "Run Build" button on my dashboard to execute a local shell script, so I can automate repetitive tasks.
- **As a developer**, I want my dashboard to work offline by fetching cached snippets from my browser's IndexedDB.

## 4. Functional Requirements

### 4.1 Frontend (Next.js Dashboard)
- **Framework**: Next.js (App Router), React, Material UI v7.
- **Pages**: Login, Overview Dashboard, Snippet Library, File Manager, Automation Hub.
- **State Hydration**: Read from `IndexedDB` on load; sync with BFF in the background.

### 4.2 BFF (Backend for Frontend - FastAPI)
- Acts as an API Gateway for the Next.js app.
- Exposes only REST endpoints to the Frontend.
- Internally orchestrates calls to the 5 microservices using appropriate protocols (REST or gRPC).

### 4.3 The 5 Core Microservices
1. **Identity Service (Port 8001)**
   - Exposes REST API.
   - Handles OAuth2 callbacks (GitHub/Google).
   - Issues JWTs (JSON Web Tokens) for session management.
   - Database: PostgreSQL (Users table).

2. **Snippet Engine (Port 8002)**
   - Exposes **gRPC** API (defined via Protocol Buffers).
   - High-throughput CRUD operations for text/code payloads.
   - Database: PostgreSQL (Snippets table).

3. **Automation Worker (Port 8003)**
   - Exposes REST API.
   - Spawns and manages local OS processes (`subprocess` in Python).
   - Monitors exit codes and runtime durations.

4. **Blob Storage Service (Port 8004)**
   - Exposes REST API.
   - Wraps the MinIO SDK. Handles file uploads and generates pre-signed download URLs.
   - Database: PostgreSQL (File metadata table) + MinIO (Binary objects).

5. **Analytics Service (Port 8005)**
   - Exposes REST API.
   - Ingests events (e.g., "Snippet created", "Script failed").
   - Aggregates data for the frontend charts (e.g., usage per language, script success rates).

## 5. Security & Authentication
- Frontend sends requests with an `Authorization: Bearer <JWT>` header to the BFF.
- BFF validates the JWT with the Identity Service before routing requests to internal microservices.
