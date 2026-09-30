"""
AdminService - statistics and platform oversight for admins.

Exposes: user list, user count, scan totals, average health score and
per-type scan counts, for the admin dashboard.
"""
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository, HealthRepository
from app.repositories.users_repository import UserRepository


class AdminService:
    def __init__(self, db) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)

    def require_admin(self, user: User) -> None:
        if not user or user.role != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")

    def stats(self) -> dict:
        return {
            "total_users": self.user_repo.count(),
            "total_scans": self._count_scans(),
            "high_risk_scans": self._count_high_risk(),
            "avg_health_score": self._avg_health(),
            "scans_by_type": self._scans_by_type(),
            "recent_scans": self._recent_scans(),
        }

    def _count_scans(self) -> int:
        from sqlalchemy import func
        from app.models.assessment import Assessment

        return self.db.query(func.count(Assessment.id)).scalar() or 0

    def _count_high_risk(self) -> int:
        from app.models.assessment import Assessment

        return self.db.query(Assessment).filter(Assessment.risk_score >= 70).count()

    def _avg_health(self) -> float:
        from sqlalchemy import func
        from app.models.health import HealthSnapshot

        avg = self.db.query(func.avg(HealthSnapshot.health_score)).scalar()
        return round(float(avg or 0), 1)

    def _scans_by_type(self) -> dict[str, int]:
        from sqlalchemy import func
        from app.models.assessment import Assessment

        rows = (self.db.query(Assessment.type, func.count(Assessment.id))
                .group_by(Assessment.type).all())
        return {t: c for t, c in rows}

    def _recent_scans(self, limit: int = 10) -> list:
        from app.models.assessment import Assessment

        return [
            {"id": a.id, "type": a.type, "prediction": a.prediction,
             "risk_score": a.risk_score, "user_id": a.user_id,
             "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in self.db.query(Assessment).order_by(Assessment.created_at.desc()).limit(limit).all()
        ]

    def users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repo.list_users(skip, limit)