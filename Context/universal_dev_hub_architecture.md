# Architecture: Universal Dev-Hub

This document contains the structural blueprints for the Universal Dev-Hub.

## 1. High-Level System Topology
This diagram illustrates the macro-architecture: how the browser, gateway, microservices, and databases connect.

```mermaid
graph TD
    %% Define styles
    classDef frontend fill:#3178c6,stroke:#fff,stroke-width:2px,color:#fff
    classDef bff fill:#009688,stroke:#fff,stroke-width:2px,color:#fff
    classDef service fill:#4caf50,stroke:#fff,stroke-width:2px,color:#fff
    classDef grpc fill:#8bc34a,stroke:#fff,stroke-width:2px,color:#fff
    classDef database fill:#ff9800,stroke:#fff,stroke-width:2px,color:#fff
    classDef storage fill:#f44336,stroke:#fff,stroke-width:2px,color:#fff

    Browser["Browser (Next.js UX)<br/>+ IndexedDB Cache"]:::frontend
    BFF["BFF (FastAPI API Gateway)"]:::bff

    Browser -- "REST (JSON) over HTTP/1.1" --> BFF

    subgraph "Local Microservices Ecosystem"
        ID["1. Identity Service<br/>(REST)"]:::service
        SNIP["2. Snippet Engine<br/>(gRPC)"]:::grpc
        AUTO["3. Automation Worker<br/>(REST)"]:::service
        BLOB["4. Blob Service<br/>(REST)"]:::service
        ANAL["5. Analytics Service<br/>(REST)"]:::service
    end

    BFF -. "Verify JWT" .-> ID
    BFF -- "REST" --> ID
    BFF == "gRPC (Protobufs)" === SNIP
    BFF -- "REST" --> AUTO
    BFF -- "REST" --> BLOB
    BFF -- "REST" --> ANAL

    PG[("PostgreSQL 16<br/>(Metadata/Text)")]:::database
    MINIO[("MinIO<br/>(S3 Binary Blob Storage)")]:::storage

    ID --> PG
    SNIP --> PG
    AUTO --> PG
    BLOB --> PG
    ANAL --> PG
    
    BLOB ==> MINIO
```

## 2. Frontend Architecture (Next.js Application)
This diagram details how the Next.js application separates routing, logic, and UI components internally.

```mermaid
graph TD
    classDef ui fill:#9c27b0,stroke:#fff,stroke-width:2px,color:#fff
    classDef logic fill:#673ab7,stroke:#fff,stroke-width:2px,color:#fff
    classDef store fill:#3f51b5,stroke:#fff,stroke-width:2px,color:#fff

    App["src/app/ (Routing)"]:::ui
    Providers["src/contexts/ (Global State)"]:::store
    Components["src/components/ (UI Atoms)"]:::ui
    Hooks["src/hooks/ (Shared Logic)"]:::logic
    Lib["src/lib/ (API Clients)"]:::logic
    IDB[("IndexedDB (Local Store)")]:::store

    App --> Providers
    App --> Components
    Components --> Hooks
    Providers --> Hooks
    Hooks --> Lib
    Lib --> IDB
    Lib --> ExternalAPI["External BFF Server"]
```

## 3. Data Flow Example: Fetching Snippets
This diagram tracks the lifecycle of a single request from the user's click to the database and back.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Component as React Component
    participant IDB as IndexedDB (Browser)
    participant BFF as API Gateway (FastAPI)
    participant Snippet as Snippet Engine (gRPC)
    participant PG as PostgreSQL

    User->>Component: Clicks "Load Snippets"
    Component->>IDB: Read cached snippets (Instant UI Update)
    IDB-->>Component: Return Stale Data
    Component->>BFF: GET /api/snippets (REST/JSON)
    BFF->>BFF: Validate Auth JWT
    BFF->>Snippet: GetSnippetsRequest (gRPC Binary Payload)
    Snippet->>PG: SELECT * FROM snippets
    PG-->>Snippet: Return Rows
    Snippet-->>BFF: GetSnippetsResponse (gRPC Binary Payload)
    BFF->>BFF: Serialize to JSON
    BFF-->>Component: HTTP 200 JSON Response
    Component->>IDB: Update Cache (Offline Sync)
    Component->>User: Re-render UI with Fresh Data
```
