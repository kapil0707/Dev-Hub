"""
=============================================================================
Blob Storage Service — MinIO File Management
=============================================================================
Port: 8004

RESPONSIBILITY:
    Wraps the MinIO SDK to provide file upload/download functionality.
    PostgreSQL stores file METADATA (name, size, MIME type, MinIO path).
    MinIO stores the actual binary file data.

WHY TWO STORES (PostgreSQL + MinIO)?
    Rule: "Store only what the DB is good at."
    - PostgreSQL: great at structured, queryable metadata
    - MinIO (S3): great at serving large binary blobs efficiently
    Never store binary blobs in PostgreSQL columns — it's slow and wastes DB storage.

DATABASE: PostgreSQL → schema: blob_storage → table: blob_storage.files
OBJECT STORE: MinIO (local) → bucket: devhub-files

RUN: uvicorn main:app --port 8004 --reload
=============================================================================
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from devhub_shared.logging.logger import get_logger

load_dotenv("../../../.env")
logger = get_logger(__name__, service_name="blob_service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Blob Storage Service starting up", extra={"port": 8004})
    # TODO (Phase 5): Initialize MinIO client and ensure bucket exists
    yield
    logger.info("Blob Storage Service shutting down")


app = FastAPI(
    title="Dev-Hub Blob Storage Service",
    description="File upload/download via MinIO S3-compatible storage.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "blob_service", "version": "0.1.0"}

# TODO (Phase 5):
# POST   /files/upload      → multipart upload → FileMetadataResponse
# GET    /files             → List[FileMetadataResponse]
# GET    /files/{id}/download → PresignedUrlResponse
# DELETE /files/{id}        → 204 No Content
