"""
AdvisorService - generates personalized, evidence-based security tips.

Tips are derived from the user's actual scan results and cyber-health
components (not generic boilerplate). For example, a weak credential
scan or HTTPS-absent URL triggers a targeted, prioritized tip.
"""
from app.models.user import User
from app.repositories.assessments_repository import AdvisorRepository, AssessmentRepository, HealthRepository


class AdvisorService:
    def __init__(self, db) -> None:
        self.db = db
        self.adv_repo = AdvisorRepository(db)
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)

    def list(self, user: User) -> list:
        return self.adv_repo.list_for_user(user.id)

    @staticmethod
    def _rule(kind: str, title: str, message: str, priority: str, category: str):
        return {"kind": kind, "title": title, "message": message,
                "priority": priority, "category": category}

    def generate_from_health(self, user: User) -> None:
        """Create (once) a set of personalized tips based on latest state."""
        latest = self.health_repo.latest(user.id)
        comps = latest.factors if latest and latest.factors else {}
        tips = []

        url_safe = comps.get("url_safety")
        if url_safe is not None and url_safe < 60:
            tips.append(self._rule("url", "Avoid suspicious links",
                                   "Some URLs you scanned showed phishing indicators. "
                                   "Hover before clicking and verify domains.", "high", "URL"))
        spam = comps.get("spam_exposure")
        if spam is not None and spam < 60:
            tips.append(self._rule("email", "Beware of phishing emails",
                                 "Your scanned emails look spammy. Never share OTPs or "
                                 "passwords via email.", "high", "EMAIL"))
        cred = comps.get("credential_strength")
        if cred is not None and cred < 70:
            tips.append(self._rule("credential", "Strengthen your passwords",
                                 "Use 12+ char passphrases with symbols and enable "
                                 "Multi-Factor Authentication everywhere.", "high", "CREDENTIALS"))
        if user.awareness_score < 60:
            tips.append(self._rule("awareness", "Improve your security awareness",
                                 "Complete a short awareness quiz to lower your risk of "
                                 "social engineering.", "medium", "AWARENESS"))

        tips.append(self._rule("general", "Enable Multi-Factor Authentication",
                             "MFA is the single most effective control against "
                             "credential theft.", "medium", "GENERAL"))

        for t in tips:
            self.adv_repo.add(user.id, t["title"], t["message"], t["category"], t["priority"])

    def mark_read(self, user: User, msg_id: int) -> None:
        self.adv_repo.mark_read(msg_id)

    def mark_all_read(self, user: User) -> None:
        self.adv_repo.clear_all_read(user.id)