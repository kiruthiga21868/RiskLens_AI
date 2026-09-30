"""
DashboardService - composes the dashboard payload from health score,
threat summary, recent activity and a 30-day trend.
"""
from fastapi import HTTPException

from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository, HealthRepository
from app.services.health_score_service import HealthScoreService


class DashboardService:
    def __init__(self, db) -> None:
        self.db = db
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)
        self.health_svc = HealthScoreService(db)

    def dashboard(self, user: User) -> dict:
        latest = self.health_repo.latest(user.id)
        if latest is None:
            # first visit: compute a baseline snapshot
            self.health_svc.compute(user)
            latest = self.health_repo.latest(user.id)

        comps = latest.factors or {
            "url_safety": latest.url_safety, "spam_exposure": latest.spam_exposure,
            "credential_strength": latest.credential_strength,
            "awareness_score": latest.awareness_score, "threat_history": latest.threat_history,
        }

        summary = self.assess_repo.summary_for_user(user.id)
        recent = self.assess_repo.list_for_user(user.id, limit=8)
        series = self.assess_repo.last_30d_series(user.id)

        return {
            "health_score": latest.health_score,
            "status": _status_label(latest.health_score),
            "trend": self.health_svc._trend(user.id),
            "components": comps,
            "threat_summary": list(summary.values()),
            "recent_activity": [_to_recent(a) for a in recent],
            "total_scans": self.assess_repo.count_for_user(user.id),
            "last_30d": series,
        }


def _status_label(score: float) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Fair"
    return "At Risk"


def _to_recent(a) -> dict:
    return {
        "id": a.id, "type": a.type, "content": a.content,
        "prediction": a.prediction, "risk_score": a.risk_score,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }