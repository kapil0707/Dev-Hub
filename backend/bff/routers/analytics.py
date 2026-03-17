import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from dependencies import get_current_user
from devhub_shared.logging.logger import get_logger

logger = get_logger(__name__, service_name="bff")
router = APIRouter(tags=["Analytics"])

ANALYTICS_SERVICE_PORT = os.getenv("ANALYTICS_SERVICE_PORT", "8005")
ANALYTICS_SERVICE_URL = f"http://127.0.0.1:{ANALYTICS_SERVICE_PORT}/events"


@router.post("/")
async def track_event(request: Request, current_user: dict = Depends(get_current_user)):
    """Proxy tracking event downstream with the authenticated user ID."""
    user_id = current_user.get("user_id")
    payload = await request.json()
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ANALYTICS_SERVICE_URL}/",
                json=payload,
                headers={"X-User-Id": str(user_id)}
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Analytics service: {exc}")
            # Do NOT fail for tracking analytics to ensure core features work even if analytics is down
            return {"status": "analytics_ignored", "reason": str(exc)}


@router.get("/metrics")
async def get_dashboard_metrics(days: int = 7, current_user: dict = Depends(get_current_user)):
    """Fetch dashboard metrics filtered down to the authenticated user."""
    user_id = current_user.get("user_id")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{ANALYTICS_SERVICE_URL}/metrics?days={days}",
                headers={"X-User-Id": str(user_id)}
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as exc:
            logger.error(f"Error communicating with Analytics service: {exc}")
            raise HTTPException(status_code=503, detail="Analytics service is unavailable")
