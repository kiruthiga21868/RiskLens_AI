"""
Startup bootstrap - runs once when the app starts.

1. Creates all database tables (idempotent).
2. Bootstraps the admin account if it does not exist.
3. Warms up the ML models so the first request is fast.

WHY HERE AND NOT AT IMPORT TIME
    Import-time side effects are a code smell and break unit tests.
    The lifespan hook in main.py is the sanctioned startup path.
"""
import logging

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base, SessionLocal, engine
from app.models import user  # noqa: F401  (register models)
from app.models.advisor import AdvisorMessage  # noqa: F401
from app.models.assessment import Assessment  # noqa: F401
from app.models.health import HealthSnapshot  # noqa: F401

logger = logging.getLogger(__name__)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")


def bootstrap_admin() -> None:
    settings = get_settings()
    db: Session = SessionLocal()
    try:
        exists = (db.query(user.User)
                  .filter(user.User.username == settings.ADMIN_USERNAME).first())
        if not exists:
            admin = user.User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                full_name="Platform Administrator",
                role="admin",
                awareness_score=90,
            )
            db.add(admin)
            db.commit()
            logger.info("Admin account '%s' bootstrapped", settings.ADMIN_USERNAME)
        else:
            logger.info("Admin account already present")
    finally:
        db.close()


def warm_models() -> None:
    from app.ml import warm_up

    warm_up()
    logger.info("ML models warmed")


def run_bootstrap() -> None:
    create_tables()
    bootstrap_admin()
    warm_models()