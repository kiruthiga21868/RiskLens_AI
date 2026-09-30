"""
Assessment ORM model - a unified record of every detection the user runs.

ONE table for URL, email and credential scans keeps reporting and the
dashboard simple. A `category` discriminator tells which AI model ran.
The `meta` JSON column stores model-specific extras (email features,
credential composition, etc.).
"""
import json
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # type in {url, email, credential}
    type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    # the raw input (URL / email text / credential)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # core AI output -- the six fields every prediction returns
    prediction: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "legitimate"
    confidence: Mapped[float] = mapped_column(Float, nullable=False)      # 0..1
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)      # 0..100
    feature_importance: Mapped[str] = mapped_column(JSON, nullable=False) # dict: feature -> value
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)

    # raw model prediction float e.g. 0.87
    raw_score: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[str] = mapped_column(JSON, nullable=True)             # extra metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="assessments")

    @property
    def details_dict(self):
        """Details can be stored as list or dict; keep a safe getter."""
        if isinstance(self.details, str):
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return {}
        return self.details or {}

    def risk_level(self) -> str:
        from app.core.config import get_settings

        s = get_settings()
        if self.risk_score >= s.HIGH_RISK_THRESHOLD * 100:
            return "high"
        if self.risk_score >= s.MEDIUM_RISK_THRESHOLD * 100:
            return "medium"
        return "low"