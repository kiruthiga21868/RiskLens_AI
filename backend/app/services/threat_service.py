"""
ThreatService - threat history listing/detail for a user.
"""
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository


class ThreatService:
    def __init__(self, db) -> None:
        self.db = db
        self.repo = AssessmentRepository(db)

    def history(self, user: User, page: int, page_size: int) -> dict:
        items = self.repo.list_for_user(user.id, skip=(page - 1) * page_size, limit=page_size)
        total = self.repo.count_for_user(user.id)
        return {
            "items": [_item(a) for a in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def detail(self, user: User, threat_id: int) -> dict:
        for a in self.repo.list_all(user.id):
            if a.id == threat_id:
                return _item(a)
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Threat not found")


def _item(a) -> dict:
    return {
        "id": a.id, "type": a.type, "content": a.content, "prediction": a.prediction,
        "confidence": a.confidence, "risk_score": a.risk_score,
        "feature_importance": a.feature_importance or {},
        "explanation": a.explanation, "recommendation": a.recommendation,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }