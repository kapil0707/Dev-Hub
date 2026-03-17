# Phase 5: Blob Storage Service — Implementation Plan

This plan details the steps to implement a dedicated File Management microservice (Blob Storage Service) powered by MinIO, integrate it with the API Gateway (BFF), and build a File Manager UI in the Next.js frontend.

## Proposed Changes

---

### Backend: Blob Storage Service (Port 8004)

The internal microservice responsible for handling file uploads, downloads, and metadata storage. It interacts directly with the local MinIO instance (S3-compatible storage) and PostgreSQL.

#### [NEW] `backend/services/blob_service/alembic.ini` and `alembic/`
- Initialize Alembic for async migrations against the `blob` schema in PostgreSQL.

#### [NEW] `backend/services/blob_service/database.py`
- Setup SQLAlchemy async engine and [get_db](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/identity/database.py#71-90) dependency.

#### [NEW] `backend/services/blob_service/models.py`
- Define `FileRecord` SQLAlchemy model mapping to `blob.files` table.
- Columns: [id](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/contexts/AuthContext.tsx#44-102) (UUID), `user_id` (UUID), `filename` (String), `content_type` (String), `size_bytes` (Integer), `path` (String S3 Key), `created_at`.

#### [NEW] `backend/services/blob_service/minio_client.py`
- Setup the `boto3` or `minio` Python SDK client to connect to `MINIO_ENDPOINT`.
- Function to ensure the `devhub-files` bucket exists on startup.
- Functions for `upload_file`, `get_presigned_url`, and `delete_file`.

#### [NEW] `backend/services/blob_service/schemas.py`
- Pydantic models: `FileUploadResponse`, `FileRecordResponse`, `FileMetadata`.

#### [NEW] `backend/services/blob_service/routers/files.py`
- `POST /files/upload`: Accepts `UploadFile`, streams it to MinIO, and creates a `FileRecord` in the database.
- `GET /files`: Returns a list of all files owned by the user.
- `GET /files/{id}/download`: Generates and returns a short-lived MinIO presigned URL for direct secure downloading.
- `DELETE /files/{id}`: Deletes the file off MinIO and removes the `FileRecord`.

#### [NEW] [backend/services/blob_service/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/services/blob_service/main.py)
- Initialize FastAPI app and include the `files` router.

---

### Backend: BFF API Gateway (Port 8000)

The API Gateway will expose the Blob Storage Service to the frontend securely.

#### [NEW] `backend/bff/routers/files.py`
- Define proxy endpoints forwarding `/api/v1/files/*` to `http://localhost:8004/files/*`.
- Ensure JWT validation middleware ([get_current_user](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/dependencies.py#30-54)) is applied. Pass the authenticated `user_id` to the downstream Blob service via a custom header (e.g., `X-User-Id`).

#### [MODIFY] [backend/bff/main.py](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/backend/bff/main.py)
- Include the `files_router` to expose the new endpoints.

---

### Frontend: Next.js Dashboard

The user interface to upload, view, and organize files.

#### [NEW] `frontend/src/lib/api/files.ts`
- Functions: `uploadFile(file: File)`, `getFiles()`, `downloadFile(id: string)`, `deleteFile(id: string)` using the `fetch` API against the BFF.

#### [NEW] `frontend/src/app/dashboard/files/page.tsx`
- **UI Components**:
  - A Data Grid / Table to show uploaded files (Name, Size, Type, Date).
  - A Drag-and-Drop or Button based File Uploader component.
  - Download and Delete action buttons per row.
- **State**: React hooks to fetch files, handle the upload progress (if applicable), and manage deletion confirmations.

#### [MODIFY] [frontend/src/app/dashboard/layout.tsx](file:///c:/Users/LENOVO/Desktop/Dump/Dev-Hub/frontend/src/app/dashboard/layout.tsx)
- Add "File Manager" link to the Dashboard Sidebar Navigation Menu.

---

## Verification Plan

### Automated / Backend Tests
1. Verify the S3 bucket is created globally in MinIO.
2. Direct API tests against `localhost:8004` to ensure files successfully land in MinIO and generate a database record.

### Manual Verification
1. Open the UI, navigate to File Manager.
2. Upload test images and text files. Ensure they appear in the UI list.
3. Verify the download functionality securely fetches the file through the presigned URL.
4. Verify file deletion removes it from both the UI and the underlying MinIO bucket.
