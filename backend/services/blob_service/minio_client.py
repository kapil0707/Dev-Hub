"""
=============================================================================
Blob Storage Service — MinIO Wrapper
=============================================================================
"""
import os
from datetime import timedelta
from minio import Minio
from dotenv import load_dotenv

# Load env variables
_service_root = os.path.dirname(os.path.abspath(__file__))
_monorepo_root = os.path.abspath(os.path.join(_service_root, "..", "..", ".."))
load_dotenv(os.path.join(_monorepo_root, ".env"))

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "devhub-files")
MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

# Initialize MinIO client
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=MINIO_USE_SSL
)

def ensure_bucket_exists():
    """Ensure the target bucket exists before doing any operations."""
    found = client.bucket_exists(MINIO_BUCKET_NAME)
    if not found:
        client.make_bucket(MINIO_BUCKET_NAME)

def upload_file_obj(object_name: str, file_data, length: int, content_type: str = "application/octet-stream"):
    """Streams a file-like object directly to S3/MinIO."""
    client.put_object(
        MINIO_BUCKET_NAME,
        object_name,
        file_data,
        length,
        content_type=content_type
    )

def get_presigned_url(object_name: str, expiration_minutes: int = 60, filename: str = None) -> str:
    """Generates a secure, temporary URL to download or view the file."""
    response_headers = None
    if filename:
        response_headers = {"response-content-disposition": f'attachment; filename="{filename}"'}
        
    return client.presigned_get_object(
        MINIO_BUCKET_NAME,
        object_name,
        expires=timedelta(minutes=expiration_minutes),
        response_headers=response_headers,
    )

def delete_object(object_name: str):
    """Deletes an object from the S3 bucket."""
    client.remove_object(MINIO_BUCKET_NAME, object_name)
