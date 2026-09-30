"""
DetectionService - orchestrates a single scan end-to-end:
    input -> ML detector -> SHAP explanation -> persist Assessment
            -> recompute Cyber Health Score -> enqueue Advisor tips.

Keeps the controller thin: the route just calls scan_type() and returns
a unified response plus the updated health snapshot.
"""
from typing import Any

from app.ml import get_credential_analyzer, get_email_detector, get_url_detector
from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository, HealthRepository

DETECTORS: dict[str, object] = {
    "url": get_url_detector,
    "email": get_email_detector,
    "credential": get_credential_analyzer,
}


class DetectionService:
    def __init__(self, db) -> None:
        self.db = db
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)

    @staticmethod
    def _detector(kind: str):
        return DETECTORS[kind]()

    def analyze(self, kind: str, raw: str) -> dict:
        """Run the matching detector, persist the result and refresh health."""
        detector = self._detector(kind)
        result = detector.analyze(raw)
        return result

    def run_and_persist(self, user: User, kind: str, raw: str) -> dict:
        detector = self._detector(kind)
        result = detector.analyze(raw)

        assessment = self.assess_repo.build(
            user_id=user.id, a_type=kind, content=raw[:2000],
            prediction=result["prediction"], confidence=result["confidence"],
            risk_score=result["risk_score"], feature_importance=result["feature_importance"],
            explanation=result["explanation"], recommendation=result["recommendation"],
            raw_score=result["raw_score"], details=result.get("details"),
        )
        saved = self.assess_repo.add(assessment)

        # Persist result and include id for the frontend history view
        result["id"] = saved.id
        result["created_at"] = saved.created_at.isoformat() if saved.created_at else None
        return result

    def run_password(self, user: User, raw: str) -> dict:
        detector = get_credential_analyzer()
        result = detector.analyze_password(raw)
        assessment = self.assess_repo.build(
            user_id=user.id, a_type="credential", content=f"<password:{len(raw)} chars>",
            prediction=result["prediction"], confidence=result["confidence"],
            risk_score=result["risk_score"], feature_importance=result["feature_importance"],
            explanation=result["explanation"], recommendation=result["recommendation"],
            raw_score=result["raw_score"], details=result.get("details"),
        )
        saved = self.assess_repo.add(assessment)
        result["id"] = saved.id
        result["created_at"] = saved.created_at.isoformat() if saved.created_at else None
        # never echo the actual password
        result["content_preview"] = f"{'*' * min(len(raw), 20)}"
        return result