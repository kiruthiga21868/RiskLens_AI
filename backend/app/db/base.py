"""
Database engine, session factory and declarative base.

WHY THIS FILE
    - A single engine/session for the whole app (SQLAlchemy 2.0).
    - `get_db()` is a FastAPI dependency that yields a session per request
      and ALWAYS closes it, even on exceptions.
    - `Base` is the root for every ORM model -> Alembic/SQLAlchemy metadata
      can see all tables from one import point.
    - SQLite fallback enables zero-setup local dev; PostgreSQL works with
      the same code (just swap DATABASE_URL).
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite needs check_same_thread=False because FastAPI runs sync endpoints
# in a threadpool. connect_args is harmless/ignored by PostgreSQL.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,  # drop stale connections (good for Postgres)
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base inherited by all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
