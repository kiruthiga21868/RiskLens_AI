"""
Assessment + health + advisor repositories (evidence / reads).

SQLAlchemy 2.0 supports lightweight aggregate queries directly in the
repository, keeping service logic clean of query plumbing.
"""
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.advisor import AdvisorMessage
from app.models.assessment import Assessment
from app.models.health import HealthSnapshot
from app.models.user import User


class AssessmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def build(user_id: int, a_type: str, content: str, prediction: str,
              confidence: float, risk_score: float, feature_importance: dict,
              explanation: str, recommendation: str, raw_score: float,
              details: dict | None = None) -> Assessment:
        return Assessment(
            user_id=user_id, type=a_type, content=content, prediction=prediction,
            confidence=confidence, risk_score=risk_score,
            feature_importance=feature_importance, explanation=explanation,
            recommendation=recommendation, raw_score=raw_score, details=details,
        )

    def add(self, assessment: Assessment) -> Assessment:
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def list_for_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[Assessment]:
        return (self.db.query(Assessment)
                .filter(Assessment.user_id == user_id)
                .order_by(Assessment.created_at.desc())
                .offset(skip).limit(limit).all())

    def list_all(self, user_id: int) -> list[Assessment]:
        return (self.db.query(Assessment)
                .filter(Assessment.user_id == user_id).all())

    def count_for_user(self, user_id: int) -> int:
        return self.db.query(Assessment).filter(Assessment.user_id == user_id).count()

    def summary_for_user(self, user_id: int) -> dict:
        """Aggregate counts by type and by risk band for one user."""
        rows = (self.db.query(Assessment.type, func.count(Assessment.id),
                              func.avg(Assessment.risk_score))
                .filter(Assessment.user_id == user_id)
                .group_by(Assessment.type).all())

        by_type: dict[str, dict] = {}
        for a_type, count, avg_risk in rows:
            band = (self.db.query(Assessment.risk_score)
                    .filter(Assessment.user_id == user_id,
                            Assessment.type == a_type).all())
            high = sum(1 for (r,) in band if r >= 70)
            medium = sum(1 for (r,) in band if 40 <= r < 70)
            low = sum(1 for (r,) in band if r < 40)
            by_type[a_type] = {"type": a_type, "count": count,
                               "avg_risk": round(float(avg_risk or 0), 1),
                               "high": high, "medium": medium, "low": low}
        return by_type

    def last_30d_series(self, user_id: int) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=30)
        rows = (self.db.query(
                func.date(Assessment.created_at).label("day"),
                func.count(Assessment.id),
                func.avg(Assessment.risk_score))
                .filter(Assessment.user_id == user_id,
                        Assessment.created_at >= cutoff)
                .group_by(func.date(Assessment.created_at))
                .all())
        return [{"date": str(d), "count": c, "avg_risk": round(float(a or 0), 1)}
                for d, c, a in rows]


class HealthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user_id: int, health_score: float, url_safety: float,
               spam_exposure: float, credential_strength: float,
               awareness_score: float, threat_history: float, factors: dict) -> HealthSnapshot:
        snap = HealthSnapshot(user_id=user_id, health_score=health_score,
                              url_safety=url_safety, spam_exposure=spam_exposure,
                              credential_strength=credential_strength,
                              awareness_score=awareness_score,
                              threat_history=threat_history, factors=factors)
        self.db.add(snap)
        self.db.commit()
        self.db.refresh(snap)
        return snap

    def latest(self, user_id: int) -> HealthSnapshot | None:
        return (self.db.query(HealthSnapshot)
                .filter(HealthSnapshot.user_id == user_id)
                .order_by(HealthSnapshot.created_at.desc())
                .first())

    def trend(self, user_id: int, limit: int = 7) -> list[dict]:
        snaps = (self.db.query(HealthSnapshot)
                 .filter(HealthSnapshot.user_id == user_id)
                 .order_by(HealthSnapshot.created_at.desc())
                 .limit(limit).all())
        return [s.to_dict() for s in reversed(snaps)]


class AdvisorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, user_id: int, title: str, message: str,
            category: str = "GENERAL", priority: str = "medium") -> AdvisorMessage:
        msg = AdvisorMessage(user_id=user_id, title=title, message=message,
                             category=category, priority=priority)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def list_for_user(self, user_id: int) -> list[AdvisorMessage]:
        return (self.db.query(AdvisorMessage)
                .filter(AdvisorMessage.user_id == user_id)
                .order_by(AdvisorMessage.priority.desc(), AdvisorMessage.created_at.desc())
                .all())

    def mark_read(self, msg_id: int) -> AdvisorMessage | None:
        msg = self.db.get(AdvisorMessage, msg_id)
        if msg:
            msg.is_read = True
            self.db.commit()
            self.db.refresh(msg)
        return msg

    def clear_all_read(self, user_id: int) -> None:
        (self.db.query(AdvisorMessage)
         .filter(AdvisorMessage.user_id == user_id, AdvisorMessage.is_read == False)  # noqa: E712
         .update({AdvisorMessage.is_read: True}))
        self.db.commit()