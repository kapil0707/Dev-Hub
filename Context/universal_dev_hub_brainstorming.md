# Brainstorming Session: Universal Dev-Hub

## 1. Problem Statement & Motivation
As an intermediate C++ developer transitioning to web development, learning a modern full-stack ecosystem (Next.js, Python FastAPI, PostgreSQL, Microservices) can be overwhelming if done without a focused, realistic project. 
The **Universal Dev-Hub** solves two problems simultaneously:
1. It provides a highly relevant, real-world development environment to learn advanced architectural patterns (BFF, gRPC, MinIO, offline-first).
2. It yields a genuinely useful local productivity tool that enhances daily development tasks.

## 2. Target Audience & Constraints
- **Primary User**: Developer (Single-tenant).
- **Environment**: 100% Local (Laptop/Desktop). No cloud dependencies. No AWS/GCP bills.
- **Goal**: Master production-grade practices (SSO, validation, inter-service communication over REST/gRPC, blob storage).

## 3. Core Feature Brainstorming
*What does a developer need locally?*
- **Snippets**: A place to store, tag, and quickly search for C++, Python, or Bash snippets.
- **Identity**: Even for local tools, practicing authentication (SSO via Google/Github) is a critical learning goal.
- **Files**: Storing architecture diagrams, PDFs of documentation, and small demo videos.
- **Automation**: Executing heavy C++ compilation scripts or Python data tasks via a button click on a web dashboard.
- **Analytics**: "How many snippets did I add? How many scripts did I run?" (A reason to use charts).

## 4. Architectural Paradigms (The "Why")
- **Why Next.js & MUI?** Familiarity established. It provides strict routing (`app/`) and production-grade UI components.
- **Why a BFF (Backend for Frontend)?** Standard industry practice to decouple the UI from backend microservice orchestration. It acts as a single gateway.
- **Why gRPC for Snippets?** Text payloads can get large. Learning to define Protobufs (similar to C++ structs/headers) bridges the gap between systems programming and web APIs.
- **Why MinIO?** To learn cloud-native blob storage (S3 API) without leaving localhost.
- **Why IndexedDB?** To implement a robust, offline-first caching layer in the browser, moving beyond simple `localStorage`.

## 5. Scope Management (MVP vs V2)
**MVP (Minimum Viable Product):**
- SSO Login.
- Basic CRUD operations for Snippets using gRPC.
- Triggering a dummy Python script via the Automation Worker.
- Uploading an image to MinIO.

**V2 (Future Scope):**
- Real-time WebSockets for streaming standard output from running processes.
- Offline-first snippet synchronization via IndexedDB.
- Cross-service correlation IDs for distributed logging.
