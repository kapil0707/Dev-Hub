"""
=============================================================================
Automation Worker — Models
=============================================================================
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID

from devhub_shared.models.base import Base


class Execution(Base):
    """
    Metadata for a local script execution.
    """
    __tablename__ = "executions"
    __table_args__ = {"schema": "automation"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_content = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="Pending") # Pending, Success, Failed
    exit_code = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
