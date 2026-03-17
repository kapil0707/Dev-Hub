import uuid
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select, func, distinct, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import EventRecord
from schemas import (
    EventCreate, EventResponse, DashboardMetricsResponse, 
    MetricSummary, TimeSeriesDataPoint, EventTypeSummary
)
from devhub_shared.logging.logger import get_logger

logger = get_logger(__name__, service_name="analytics")
router = APIRouter(tags=["Analytics"])

@router.post("/", response_model=EventResponse)
async def track_event(
    event: EventCreate,
    x_user_id: Optional[str] = Header(None, description="Injected by BFF if authenticated"),
    db: AsyncSession = Depends(get_db)
):
    """Record a generic telemetry event."""
    user_id = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError:
            pass
            
    record = EventRecord(
        user_id=user_id,
        event_type=event.event_type,
        payload=event.payload
    )
    
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return record

@router.get("/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    days: int = Query(7, description="Days to look back"),
    x_user_id: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Returns aggregated metadata spanning `days` for the dashboard overview."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    user_id = None
    if x_user_id:
        try:
            user_id = uuid.UUID(x_user_id)
        except ValueError:
            pass

    # Build base where clause
    base_filters = [EventRecord.created_at >= cutoff]
    if user_id:
        base_filters.append(EventRecord.user_id == user_id)
        
    # Total Events
    total_query = select(func.count(EventRecord.id)).where(*base_filters)
    total_result = await db.execute(total_query)
    total_events = total_result.scalar() or 0
    
    # Active Users
    users_query = select(func.count(distinct(EventRecord.user_id))).where(
        EventRecord.created_at >= cutoff,
        EventRecord.user_id.isnot(None)
    )
    users_result = await db.execute(users_query)
    active_users = users_result.scalar() or 0
    
    # Events By Type
    types_query = select(
        EventRecord.event_type, 
        func.count(EventRecord.id).label('count')
    ).where(*base_filters).group_by(EventRecord.event_type)
    
    types_result = await db.execute(types_query)
    by_type = [EventTypeSummary(event_type=row[0], count=row[1]) for row in types_result.all()]
    
    # Time Series (Events by Day)
    # Using Postgres date_trunc
    ts_query = select(
        func.date_trunc('day', EventRecord.created_at).label('day'),
        func.count(EventRecord.id).label('count')
    ).where(*base_filters).group_by(text("1")).order_by(text("1"))
    
    ts_result = await db.execute(ts_query)
    timeseries_map = {}
    
    for row in ts_result.all():
        date_obj = row[0]
        count = row[1]
        
        if isinstance(date_obj, datetime):
            formatted_date = date_obj.strftime("%b %d")
            timeseries_map[formatted_date] = count

    # Fill in blanks to ensure the chart looks continuous
    timeseries = []
    for i in range(days):
        target_date = datetime.now(timezone.utc) - timedelta(days=days - 1 - i)
        formatted_date = target_date.strftime("%b %d")
        count = timeseries_map.get(formatted_date, 0)
        timeseries.append(TimeSeriesDataPoint(date=formatted_date, count=count))
            
    return DashboardMetricsResponse(
        summary=MetricSummary(total_events=total_events, active_users=active_users),
        timeseries=timeseries,
        by_type=by_type
    )
