"""
API router aggregator.

Every feature module exposes its own APIRouter. This file mounts them all
under the versioned /api/v1 prefix. Adding a new feature later = one line.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    advisor,
    auth,
    dashboard,
    detections,
    health,
    reports,
    threats,
)

api_router = APIRouter()

# Feature modules are registered here, in order
api_router.include_router(health.router)          # system health
api_router.include_router(auth.router)            # register / login / refresh
api_router.include_router(dashboard.router)       # dashboard + awareness
api_router.include_router(detections.router)      # url / email / credential scans
api_router.include_router(advisor.router)         # personalized security tips
api_router.include_router(threats.router)         # threat history
api_router.include_router(reports.router)         # CSV / PDF reports
api_router.include_router(admin.router)           # admin dashboard