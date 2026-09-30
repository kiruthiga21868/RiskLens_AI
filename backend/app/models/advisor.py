"""
Advisor message model - personalized security tips generated for a user.

Each tip has a category (URL, EMAIL, CREDENTIALS, AWARENESS, GENERAL),
a priority level and whether the user has acted on it yet.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AdvisorMessage(Base):
    __tablename__ = "advisor_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(20), default="GENERAL")
    priority: Mapped[str] = mapped_column(String(10), default="medium")  # low|medium|high
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")