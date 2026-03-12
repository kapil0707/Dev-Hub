# System Design Document (SDD): Universal Dev-Hub

## 1. Database Schema (PostgreSQL 16)

This schema is designed using standard relational principles. Since this is a local app, all tables reside in a single Postgres database instance, accessed by the respective microservices.

### Table: `users` (Managed by Identity Service)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| [id](file:///c:/Users/LENOVO/Desktop/Dump/Repo/material-kit-react/src/contexts/user-context.tsx#22-56) | UUID | PRIMARY KEY | Unique identifier. |
| `email` | VARCHAR | UNIQUE, NOT NULL | User's email (from Google/Github). |
| `name` | VARCHAR | NOT NULL | Display name. |
| `avatar_url` | VARCHAR | | Profile picture URL. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation time. |

### Table: `snippets` (Managed by Snippet Engine)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| [id](file:///c:/Users/LENOVO/Desktop/Dump/Repo/material-kit-react/src/contexts/user-context.tsx#22-56) | UUID | PRIMARY KEY | Unique identifier. |
| `user_id` | UUID | FOREIGN KEY(users.id) | Owner of the snippet. |
| `title` | VARCHAR | NOT NULL | Human-readable title. |
| `language` | VARCHAR | NOT NULL | e.g., 'python', 'bash', 'javascript'. |
| `code` | TEXT | NOT NULL | The actual code content. |
| `tags` | VARCHAR[] | | Array of strings for searching. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation time. |

### Table: `files` (Managed by Blob Storage Service)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| [id](file:///c:/Users/LENOVO/Desktop/Dump/Repo/material-kit-react/src/contexts/user-context.tsx#22-56) | UUID | PRIMARY KEY | Unique identifier. |
| `user_id` | UUID | FOREIGN KEY(users.id) | Owner of the file. |
| `original_name`| VARCHAR | NOT NULL | e.g., 'architecture.png'. |
| `mime_type` | VARCHAR | NOT NULL | e.g., 'image/png'. |
| `size_bytes` | BIGINT | NOT NULL | File size. |
| `minio_path` | VARCHAR | NOT NULL | The path/key to retrieve the actual file from MinIO. |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Record creation time. |

### Table: `executions` (Managed by Automation Worker & Analytics)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| [id](file:///c:/Users/LENOVO/Desktop/Dump/Repo/material-kit-react/src/contexts/user-context.tsx#22-56) | UUID | PRIMARY KEY | Unique identifier. |
| `snippet_id` | UUID | FOREIGN KEY(snippets.id)| The script that was run (optional). |
| `status` | VARCHAR | NOT NULL | 'SUCCESS', 'FAILED', 'RUNNING'. |
| `duration_ms` | INTEGER | | How long the script took to run. |
| `exit_code` | INTEGER | | Process exit code (0 means success). |
| `executed_at` | TIMESTAMP | DEFAULT NOW() | Time the script was triggered. |

---

## 2. Analytics Interface (Dashboard Layout)

The Next.js frontend will use Material UI (MUI) structural components to build a "Command Center" dashboard mirroring professional tools like Vercel or Datadog.

### 2.1 Top Metrics Area (`Grid container` with `Card` components)
Four primary summary cards at the top of the screen:
1. **Total Snippets**: Large typography showing total count.
2. **Storage Used**: Data pulled from MinIO (e.g., "450 MB").
3. **Scripts Run (Today)**: Count from the `executions` table.
4. **Success Rate**: (Successful Executions / Total Executions) * 100%. Highlighted in Green if > 95%, Red if lower.

### 2.2 Main Chart Area (`Grid lg={8}`)
- **Component**: React-ApexCharts (Area Chart).
- **Data Series**: "Daily Executions over the last 30 days".
- **Purpose**: Visualizes how often you are using your local automation tools over time.

### 2.3 Recent Activity Feed (`Grid lg={4}`)
- **Component**: MUI `List` and `ListItem`.
- **Content**: A chronological feed of events.
    - *Example*: "🟢 Script 'DB Backup' completed in 1.2s"
    - *Example*: "🔴 Script 'Data Clean' failed (Exit Code 1)"
    - *Example*: "📝 Added new Python snippet"

---

## 3. Communication Protocols Reference

### 3.1 BFF to Snippet Engine (gRPC)
**Service Definition (`snippet.proto`)**:
```protobuf
syntax = "proto3";

service SnippetService {
  rpc CreateSnippet (SnippetRequest) returns (SnippetResponse);
  rpc GetSnippets (SearchRequest) returns (SnippetListResponse);
}

message SnippetRequest {
  string title = 1;
  string language = 2;
  string code = 3;
}
// Note: Binary transfer ensures very fast parsing of large code blocks.
```

### 3.2 Frontend to BFF (REST / JSON)
**Endpoint**: `GET /api/v1/analytics/summary`
**Response Payload**:
```json
{
  "total_snippets": 142,
  "storage_bytes": 450000000,
  "total_executions_today": 12,
  "success_rate": 0.98
}
```
