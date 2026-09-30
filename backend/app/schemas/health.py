"""
Health endpoint response schema.

WHY A SCHEMA FILE
    Schemas define the exact shape of API requests/responses using
    Pydantic. This gives us:
      1. Automatic request validation (reject bad payloads early).
      2. Automatic response serialization.
      3. Self-documenting Swagger/OpenAPI UI.
"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Structure returned by GET /api/v1/health."""

    status: str
    service: str
    version: str
    environment: str
    python: str
    uptime_seconds: float
