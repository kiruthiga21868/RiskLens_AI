"""
Advisor + history + report + admin schemas.
"""
from datetime import datetime

from pydantic import BaseModel


class AdvisorMessageOut(BaseModel):
    id: int
    title: str
    message: str
    category: str
    priority: str
    is_read: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class HistoryItem(BaseModel):
    id: int
    type: str
    content: str
    prediction: str
    confidence: float
    risk_score: float
    explanation: str
    recommendation: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class HistoryPage(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int


class UserAdminOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    awareness_score: int
    created_at: datetime | None = None
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class AdminStats(BaseModel):
    total_users: int
    total_scans: int
    high_risk_scans: int
    avg_health_score: float
    scans_by_type: dict[str, int]
    scans_last_30d: int