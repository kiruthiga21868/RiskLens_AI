"""
RiskLens AI - FastAPI application entrypoint.

WHY THIS FILE
    main.py is the process bootstrap: it creates the FastAPI app,
    wires configuration, logging, middleware (CORS today, JWT later),
    and mounts the versioned API router.

WHY LIFESPAN
    The lifespan context manager runs code on startup/shutdown - the
    correct place to initialize DB connections and ML models (later
    sprints) instead of doing it at import time.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.bootstrap import run_bootstrap
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()
setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle - runs on startup and shutdown."""
    logger.info("Starting %s v%s (debug=%s)", settings.APP_NAME, settings.APP_VERSION, settings.DEBUG)
    run_bootstrap()  # tables, admin account, ML warm-up
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered cybersecurity risk assessment platform: "
    "URL threat detection, email spam detection, credential risk "
    "analysis and explainable AI scoring.",
    # Custom OpenAPI path lives under the API prefix
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- CORS: allows the React frontend to call this API from a browser ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mount the versioned API router under /api/v1 ---
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"], summary="Root")
def root() -> dict:
    """Simple landing message so / is not a 404."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "openapi": settings.API_V1_PREFIX + "/openapi.json",
    }
