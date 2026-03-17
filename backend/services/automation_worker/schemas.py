"""
=============================================================================
Automation Worker — Pydantic Schemas
=============================================================================
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScriptRunRequest(BaseModel):
    """
    Payload from the frontend to run a script.
    """
    script_content: str = Field(..., description="The bash/shell script to execute")


class ExecutionResponse(BaseModel):
    """
    Response model for a script execution.
    """
    id: uuid.UUID
    script_content: str
    status: str
    exit_code: Optional[int]
    output: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

