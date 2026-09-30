"""Central model exports - import every model here so Base.metadata sees all tables."""
from app.models.advisor import AdvisorMessage
from app.models.assessment import Assessment
from app.models.health import HealthSnapshot
from app.models.user import User

__all__ = ["User", "Assessment", "HealthSnapshot", "AdvisorMessage"]