# Full-Stack Architectural Context: Material Kit React Deep Dive

## I. Core Tech Stack (Local Production-Grade)
- **Frontend Framework**: Next.js 15.3 (App Router)
- **UI Engine**: React 19.1
- **Design System**: Material UI (MUI) 7.1 + Emotion (CSS-in-JS)
- **Icons**: Phosphor Icons (React-based)
- **Type Safety**: TypeScript 5.8
- **Form/Schema**: React Hook Form + Zod (Runtime validation)
- **Date Handling**: Day.js
- **Backend (Proposed)**: Python 3.12 + FastAPI
- **Database (Proposed)**: PostgreSQL 16 (Running via Docker or Local Service)

## II. Architectural & Design Patterns (Advanced)
- **State Hydration (Offline-First)**: Using `IndexedDB` (via `idb` or `Dexie.js`) for local persistence. Strategy: UI reads from IndexedDB first; a background worker synchronizes with the BFF when network is restored.
- **BFF (Backend for Frontend)**: A FastAPI layer specifically for the Next.js app. Responsibilities: Aggregating microservice data, security headers, and simplified API surface.
- **Inter-Service Comm**: 
    - **REST/JSON**: For the Public/BFF API.
    - **gRPC**: For high-performance communication between the BFF and at least one internal Microservice (e.g., the Snippet Engine or Analytics Service).
- **Logging**: Implementation of **Structured Logging** (JSON format) across all services, with a unified correlation ID to trace requests through the microservice chain.
- **Methodology (BMAD)**: Aligned with "Big Model Architecture & Development" principles—focusing on structural integrity, semantic documentation, and decoupling.

## III. Target Project: "Universal Dev-Hub"
**Objective**: Build a local developer productivity suite that leverages multiple modern protocols and storage strategies.
- **Frontend**: Next.js Dashboard mirroring Material Kit React patterns.
- **BFF**: FastAPI orchestrator.
- **Microservices**:
    1. **Auth Service (REST)**: PostgreSQL-backed user management.
    2. **Snippet Engine (gRPC)**: Optimized code storage (The gRPC learning component).
    3. **Automation Worker**: Python-based runner for local shell/C++ scripts.
- **Storage**: Postgres (Source of Truth) + IndexedDB (Local Cache/Offline Sync).

## IV. User Profile & Learning Goals
- **Profile**: Intermediate C++ Developer (Transitioning to Web Architect).
- **Primary Goals**: Master Next.js/React Syntax, Auth Workflows, Microservices (REST/gRPC), and Offline-First State management.
- **Environment**: 100% Local (Postgres, Python, Node.js).


