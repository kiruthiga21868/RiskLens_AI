"""
Health controller - the API "controller" layer.

WHY THIS LAYER
    The controller is a thin HTTP adapter: it receives the FastAPI
    request, delegates real work to the service, and returns the
    validated response schema. Keeping it thin means business logic
    changes never require HTTP-level rewrites.
"""
from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])

# One shared instance per process (dependency injection is a later
# refinement; a module-level singleton is acceptable here)
health_service = HealthService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns application status, version and uptime. "
    "Used by load balancers, Docker healthchecks and monitoring tools.",
)
def get_health() -> HealthResponse:
    """HTTP GET /api/v1/health -> returns the health payload."""
    return HealthResponse(**health_service.get_health())
