"""
Dashboard / health-score schemas.
"""
from datetime import datetime

from pydantic import BaseModel


class AwarenessUpdate(BaseModel):
    """POST /api/v1/dashboard/awareness - user submits quiz score."""

    score: int  # 0-100


class ComponentScores(BaseModel):
    url_safety: float
    spam_exposure: float
    credential_strength: float
    awareness_score: float
    threat_history: float


class HealthScoreOut(BaseModel):
    id: int
    user_id: int
    health_score: float
    components: ComponentScores
    factors: dict
    created_at: datetime | None = None


class ThreatSummaryItem(BaseModel):
    type: str
    count: int
    high: int
    medium: int
    low: int
    avg_risk: float


class RecentActivityItem(BaseModel):
    id: int
    type: str
    content: str
    prediction: str
    risk_score: float
    created_at: datetime | None = None


class DashboardResponse(BaseModel):
    health_score: float
    status: str
    trend: str
    components: ComponentScores
    threat_summary: list[ThreatSummaryItem]
    recent_activity: list[RecentActivityItem]
    total_scans: int
    last_30d: list[dict]