from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WebhookPayload(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None

class LeadOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    source: Optional[str]
    message: Optional[str]
    country: Optional[str]
    tags: Optional[str]
    assigned_team: Optional[str]
    status: str
    is_duplicate: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class LeadStatusUpdate(BaseModel):
    status: str

class DashboardStats(BaseModel):
    total_leads: int
    today_leads: int
    duplicate_count: int
    conversion_count: int
    sources: dict
    leads_over_time: List[dict]