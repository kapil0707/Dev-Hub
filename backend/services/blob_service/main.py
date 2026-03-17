"""
=============================================================================
Blob Storage Service — Main Application
=============================================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.files import router as files_router
import minio_client

# Ensure MinIO bucket exists upon startup
try:
    minio_client.ensure_bucket_exists()
except Exception as e:
    import logging
    logging.warning(f"Could not initialize MinIO bucket on startup: {e}")

app = FastAPI(title="DevHub Blob Storage Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router, prefix="/files")

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "blob_service"}
