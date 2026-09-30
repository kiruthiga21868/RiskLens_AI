"""
HealthService - demonstrates the SERVICE layer.

WHY A SERVICE LAYER
    Controllers (routes) should only parse requests and return
    responses. All business logic lives in services. This follows the
    Single Responsibility Principle: a route knows HTTP, a service
    knows the domain. It also makes logic unit-testable without HTTP.

WHY A CLASS
    We store the process start time as instance state so uptime can be
    reported. Using a class keeps related behavior + state together.
"""
import platform
import time

from app.core.config import get_settings


class HealthService:
    """Reports application health / uptime information."""

    def __init__(self) -> None:
        # Record the moment this service object was created
        self._started_at: float = time.time()

    def get_health(self) -> dict:
        """
        Compose the health payload from config + runtime info.

        Returns:
            dict with status, service name, version, environment,
            Python version and uptime in seconds.
        """
        settings = get_settings()
        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "python": platform.python_version(),
            "uptime_seconds": round(time.time() - self._started_at, 2),
        }
