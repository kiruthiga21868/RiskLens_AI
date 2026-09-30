"""
User ORM model.

Stores authentication accounts. Passwords are stored ONLY as bcrypt hashes.
A nullable last_login lets the admin dashboard show account activity.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    role: Mapped[str] = mapped_column(Enum("user", "admin", name="user_role"), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    awareness_score: Mapped[int] = mapped_column(default=50)  # 0-100 quiz score
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")