"""
Health snapshot model - stores the latest Cyber Health Score per user,
including the five component scores used to derive it.

The JSON `factors` column keeps the audit trail of which assessments
contributed to the score.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    health_score: Mapped[float] = mapped_column(Float, nullable=False)          # 0..100
    url_safety: Mapped[float] = mapped_column(Float, default=50.0)
    spam_exposure: Mapped[float] = mapped_column(Float, default=50.0)
    credential_strength: Mapped[float] = mapped_column(Float, default=50.0)
    awareness_score: Mapped[float] = mapped_column(Float, default=50.0)
    threat_history: Mapped[float] = mapped_column(Float, default=50.0)
    factors: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "health_score": round(self.health_score, 1),
            "components": {
                "url_safety": round(self.url_safety, 1),
                "spam_exposure": round(self.spam_exposure, 1),
                "credential_strength": round(self.credential_strength, 1),
                "awareness_score": round(self.awareness_score, 1),
                "threat_history": round(self.threat_history, 1),
            },
            "factors": self.factors or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }