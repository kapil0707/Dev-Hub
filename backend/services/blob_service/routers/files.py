"""
=============================================================================
Blob Storage Service — Files Router
=============================================================================
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import FileRecord
from schemas import FileRecordResponse, FileUploadResponse, PresignedUrlResponse
import minio_client
from devhub_shared.logging.logger import get_logger

logger = get_logger(__name__, service_name="blob_service")
router = APIRouter(tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    x_user_id: str = Header(..., description="The authenticated user ID injected by the BFF"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file. The file is streamed straight to MinIO and metadata is saved to PostgreSQL.
    """
    user_id = uuid.UUID(x_user_id)
    
    # Read the file to memory to obtain its size for MinIO
    file_bytes = await file.read()
    length = len(file_bytes)
    
    # Seek back so MinIO can read it from the start
    await file.seek(0)
    
    logger.info(f"Received file upload '{file.filename}' ({length} bytes) for user {user_id}")
    
    # Unique object key: {user_id}/{uuid}-{filename}
    object_name = f"{user_id}/{uuid.uuid4()}-{file.filename}"
    
    try:
        # MinIO natively accepts the un-async `file.file` as an IO stream
        minio_client.upload_file_obj(
            object_name=object_name,
            file_data=file.file,
            length=length,
            content_type=file.content_type or "application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Failed to upload to MinIO: {e}")
        raise HTTPException(status_code=500, detail=f"Storage provider error: {e}")
        
    # Save Record metadata to the database
    file_record = FileRecord(
        user_id=user_id,
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=length,
        path=object_name
    )
    
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    
    return FileUploadResponse(
        message="File uploaded successfully",
        file=file_record
    )


@router.get("/", response_model=List[FileRecordResponse])
async def list_files(
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """List all file records owned by the calling user."""
    user_id = uuid.UUID(x_user_id)
    stmt = select(FileRecord).where(FileRecord.user_id == user_id).order_by(FileRecord.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{file_id}/download", response_model=PresignedUrlResponse)
async def get_download_url(
    file_id: uuid.UUID,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Generate a temporary URL for the client to download the file directly."""
    user_id = uuid.UUID(x_user_id)
    stmt = select(FileRecord).where(FileRecord.id == file_id, FileRecord.user_id == user_id)
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        url = minio_client.get_presigned_url(file_record.path, filename=file_record.filename)
        return PresignedUrlResponse(url=url)
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download link")


@router.delete("/{file_id}")
async def delete_file(
    file_id: uuid.UUID,
    x_user_id: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file from both MinIO and PostgreSQL."""
    user_id = uuid.UUID(x_user_id)
    stmt = select(FileRecord).where(FileRecord.id == file_id, FileRecord.user_id == user_id)
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        minio_client.delete_object(file_record.path)
    except Exception as e:
        logger.warning(f"Failed to delete object {file_record.path} from MinIO: {e}")
        # Proceed to delete from db anyway
        
    await db.delete(file_record)
    await db.commit()
    return {"message": "File deleted"}
