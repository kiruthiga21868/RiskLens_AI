"""
Central application configuration using pydantic-settings.

WHY THIS FILE EXISTS
    Enterprise apps never hardcode credentials or URLs in code. All
    environment-specific values come from the .env file / environment
    variables, loaded and validated once here, then reused everywhere
    via get_settings().

WHY pydantic-settings
    - Auto-reads .env files (no manual dotenv parsing).
    - Validates types (e.g. CORS_ORIGINS must be a valid list).
    - Fields are typed -> IDE autocomplete + runtime safety.

WHY lru_cache
    Settings are parsed once and cached for the process lifetime,
    which is faster and guarantees a single consistent config object.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

# Absolute path to the project root (…/backend/app/core -> parents[3] = project root).
# Resolving .env relative to this file makes the app location-independent:
# it works no matter which directory you launch uvicorn from.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """All configuration values for RiskLens AI."""

    # --- Application metadata ---
    APP_NAME: str = "RiskLens AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # --- API ---
    API_V1_PREFIX: str = "/api/v1"

    # --- Database (used from Sprint 3 onwards) ---
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/risklens"

    # --- JWT Authentication (used from Sprint 2 onwards) ---
    JWT_SECRET_KEY: str = "dev-only-secret-key-please-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Bootstrap admin (created at startup if absent) ---
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@risklens.ai"
    ADMIN_PASSWORD: str = "Admin@123456"

    # --- Threat detection thresholds ---
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4

    # --- CORS: which frontend origins may call the API ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ORIGIN_REGEX: str | None = None

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",  # absolute path -> CWD-independent
        env_file_encoding="utf-8",
        case_sensitive=True,      # APP_NAME != app_name
        extra="ignore",           # ignore unknown variables gracefully
    )

    @model_validator(mode="after")
    def _pin_sqlite_path(self) -> "Settings":
        # Make a relative SQLite path absolute so the DB is created in
        # backend/risklens.db no matter which directory uvicorn runs from.
        if self.DATABASE_URL.startswith("sqlite:///"):
            raw = self.DATABASE_URL.replace("sqlite:///", "", 1)
            if raw and not raw.startswith("/") and not (len(raw) > 1 and raw[1] == ":"):
                self.DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'backend' / raw).as_posix()}"
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the singleton Settings instance (cached after first call)."""
    return Settings()
