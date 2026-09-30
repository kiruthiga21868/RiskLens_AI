"""
Cyber Health Score engine.

The score is a weighted blend of five components:
    URL safety, Spam exposure, Credential strength, Awareness, Threat history.

Derived per-user from their stored assessments + awareness score. Returns
both the numeric score and a human status/trend label.

WEIGHTS (industry-typical for a "posture score"):
    url_safety            0.30
    spam_exposure         0.20
    credential_strength   0.20
    awareness_score       0.15
    threat_history        0.15
"""
from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository, HealthRepository

WEIGHTS = {"url": 0.30, "email": 0.20, "credential": 0.20, "awareness": 0.15, "threat_history": 0.15}


class HealthScoreService:
    def __init__(self, db) -> None:
        self.db = db
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)

    def _url_safety(self, user_id: int) -> float:
        scores = [a.risk_score for a in self.assess_repo.list_all(user_id) if a.type == "url"]
        if not scores:
            return 75.0
        return 100.0 - sum(scores) / len(scores)

    def _spam_exposure(self, user_id: int) -> float:
        scores = [a.risk_score for a in self.assess_repo.list_all(user_id) if a.type == "email"]
        if not scores:
            return 75.0
        return 100.0 - sum(scores) / len(scores)

    def _credential_strength(self, user_id: int) -> float:
        scores = [a.risk_score for a in self.assess_repo.list_all(user_id) if a.type == "credential"]
        if not scores:
            return 75.0
        return 100.0 - sum(scores) / len(scores)

    def _threat_history(self, user_id: int) -> float:
        """Punish when many high-risk assessments exist, reward clean history."""
        assessments = self.assess_repo.list_all(user_id)
        count = len(assessments)
        if count == 0:
            return 80.0
        highs = sum(1 for a in assessments if a.risk_score >= 70)
        exposure = highs / count
        return max(20.0, 85.0 - exposure * 65.0)

    def compute(self, user) -> dict:
        """Compute the five components, persist a snapshot, return the result."""
        awareness = user.awareness_score
        uid = user.id

        components = {
            "url_safety": round(self._url_safety(uid), 1),
            "spam_exposure": round(self._spam_exposure(uid), 1),
            "credential_strength": round(self._credential_strength(uid), 1),
            "awareness_score": round(float(awareness), 1),
            "threat_history": round(self._threat_history(uid), 1),
        }

        score = round(
            WEIGHTS["url"] * components["url_safety"]
            + WEIGHTS["email"] * components["spam_exposure"]
            + WEIGHTS["credential"] * components["credential_strength"]
            + WEIGHTS["awareness"] * components["awareness_score"]
            + WEIGHTS["threat_history"] * components["threat_history"],
            1,
        )

        # HealthSnapshot expects separate url/safety... columns and a factors JSON
        factors = {f"{k}": v for k, v in components.items()}
        snap = self.health_repo.create(
            user_id=uid,
            health_score=score,
            url_safety=components["url_safety"],
            spam_exposure=components["spam_exposure"],
            credential_strength=components["credential_strength"],
            awareness_score=components["awareness_score"],
            threat_history=components["threat_history"],
            factors=factors,
        )

        status = ("Excellent" if score >= 80 else "Good" if score >= 60
                  else "Fair" if score >= 40 else "At Risk")
        trend = self._trend(uid)
        return {"health_score": score, "status": status, "trend": trend,
                "components": components, "snapshot": snap.to_dict()}

    def _trend(self, user_id: int) -> str:
        series = self.health_repo.trend(user_id, limit=5)
        if len(series) < 2:
            return "stable"
        delta = series[-1]["health_score"] - series[0]["health_score"]
        return "improving" if delta >= 1 else ("declining" if delta <= -1 else "stable")

    def update_awareness(self, user, score: int) -> float:
        """Persist a new awareness score, recompute the health snapshot."""
        user.awareness_score = max(0, min(100, score))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.compute(user)["health_score"]