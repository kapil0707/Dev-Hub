"""
=============================================================================
BFF — Automation Worker Proxy
=============================================================================
"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from devhub_shared.logging.logger import get_logger
from dependencies import get_current_user

logger = get_logger(__name__, service_name="bff")

router = APIRouter()

AUTOMATION_URL = os.getenv("AUTOMATION_URL", "http://localhost:8003/scripts")


@router.post("/run")
async def proxy_run_script(request: Request, user=Depends(get_current_user)):
    """
    Proxies script execution request to Automation Worker.
    Requires authentication.
    """
    payload = await request.json()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTOMATION_URL}/run", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Failed to reach Automation Worker: {e}")
            raise HTTPException(status_code=503, detail="Automation Worker unavailable")


@router.get("/executions")
async def proxy_list_executions(user=Depends(get_current_user)):
    """
    Proxies request for execution list to Automation Worker.
    Requires authentication.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTOMATION_URL}/executions")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Failed to reach Automation Worker: {e}")
            raise HTTPException(status_code=503, detail="Automation Worker unavailable")


@router.get("/executions/{execution_id}")
async def proxy_get_execution(execution_id: str, user=Depends(get_current_user)):
    """
    Proxies request for a specific execution to Automation Worker.
    Requires authentication.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTOMATION_URL}/executions/{execution_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            logger.error(f"Failed to reach Automation Worker: {e}")
            raise HTTPException(status_code=503, detail="Automation Worker unavailable")
