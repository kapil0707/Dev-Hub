"""
=============================================================================
Blob Storage Service — Pydantic Schemas
=============================================================================
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class FileRecordResponse(BaseModel):
    """Schema for returning file metadata."""
    id: UUID
    user_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """Schema for upload response."""
    message: str
    file: FileRecordResponse


class PresignedUrlResponse(BaseModel):
    """Schema for returning a download url."""
    url: str
