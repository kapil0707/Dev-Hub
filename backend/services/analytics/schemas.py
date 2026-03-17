from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID

class EventCreate(BaseModel):
    event_type: str
    payload: Optional[Dict[str, Any]] = None

class EventResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    event_type: str
    payload: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MetricSummary(BaseModel):
    total_events: int
    active_users: int

class TimeSeriesDataPoint(BaseModel):
    date: str
    count: int

class EventTypeSummary(BaseModel):
    event_type: str
    count: int

class DashboardMetricsResponse(BaseModel):
    summary: MetricSummary
    timeseries: List[TimeSeriesDataPoint]
    by_type: List[EventTypeSummary]
