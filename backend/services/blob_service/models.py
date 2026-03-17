"""
=============================================================================
Blob Storage Service — Database Models
=============================================================================
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID

# Import Base from the shared library
from devhub_shared.models.base import Base

class FileRecord(Base):
    """
    Represents a file uploaded securely by a user and stored in MinIO.
    This metadata record lives in PostgreSQL within the 'blob' schema.
    """
    __tablename__ = "files"
    __table_args__ = {"schema": "blob"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    path = Column(String, nullable=False)  # Map to the object key in MinIO
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
