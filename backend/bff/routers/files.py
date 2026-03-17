"""
=============================================================================
BFF Gateway — Files Router Proxy
=============================================================================
"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File
from dependencies import get_current_user
from devhub_shared.logging.logger import get_logger

logger = get_logger(__name__, service_name="bff")
router = APIRouter(tags=["Files"])

BLOB_SERVICE_PORT = os.getenv("BLOB_SERVICE_PORT", "8004")
BLOB_SERVICE_URL = f"http://127.0.0.1:{BLOB_SERVICE_PORT}/files"


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Proxy an upload file request to the downstream Blob Storage Service.
    We pass the file data directly as a multipart stream.
    """
    user_id = current_user.get("user_id")
    
    file_bytes = await file.read()
    
    # Send the request to the upstream Blob Service
    async with httpx.AsyncClient() as client:
        try:
            # We reconstruct the multipart form data for the upstream service
            files = {'file': (file.filename, file_bytes, file.content_type)}
            
            resp = await client.post(
                f"{BLOB_SERVICE_URL}/upload",
                files=files,
                headers={"X-User-Id": str(user_id)}
            )
            
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
                
            try:
                return resp.json()
            except Exception as e:
                logger.error(f"Failed to decode upstream JSON: status={resp.status_code}, text=\"{resp.text}\"")
                raise HTTPException(status_code=500, detail=f"Invalid upstream JSON: {resp.text}")
        except HTTPException:
            raise
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Blob service: {exc}")
            raise HTTPException(status_code=503, detail="File service is unavailable")
        except Exception as e:
            import traceback
            logger.error(f"Upload proxy failed: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_files(current_user: dict = Depends(get_current_user)):
    """Fetch the list of file records."""
    user_id = current_user.get("user_id")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{BLOB_SERVICE_URL}/",
                headers={"X-User-Id": str(user_id)}
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.json())
            return resp.json()
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Blob service: {exc}")
            raise HTTPException(status_code=503, detail="File service is unavailable")


@router.get("/{file_id}/download")
async def generate_presigned_url(file_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch a presigned URL from the Blob service."""
    user_id = current_user.get("user_id")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{BLOB_SERVICE_URL}/{file_id}/download",
                headers={"X-User-Id": str(user_id)}
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Blob service: {exc}")
            raise HTTPException(status_code=503, detail="File service is unavailable")


@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user)):
    """Proxy the delete request."""
    user_id = current_user.get("user_id")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(
                f"{BLOB_SERVICE_URL}/{file_id}",
                headers={"X-User-Id": str(user_id)}
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Blob service: {exc}")
            raise HTTPException(status_code=503, detail="File service is unavailable")
