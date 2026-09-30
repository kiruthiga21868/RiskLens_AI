"""
ML module - feature engineering, surrogate models and SHAP explainability.

Public API:
    get_url_detector()        -> URLDetector
    get_email_detector()      -> EmailDetector
    get_credential_analyzer() -> CredentialAnalyzer
    warm_up()                 -> build all models once at startup
"""
from app.ml.detectors import CredentialAnalyzer, EmailDetector, URLDetector

_instances = None


def _ensure() -> dict:
    global _instances
    if _instances is None:
        _instances = {
            "url": URLDetector(),
            "email": EmailDetector(),
            "credential": CredentialAnalyzer(),
        }
    return _instances


def get_url_detector() -> URLDetector:
    return _ensure()["url"]


def get_email_detector() -> EmailDetector:
    return _ensure()["email"]


def get_credential_analyzer() -> CredentialAnalyzer:
    return _ensure()["credential"]


def warm_up() -> None:
    """Pre-build all surrogate models at startup for fast first requests."""
    d = _ensure()
    for k in ("url", "email", "credential"):
        d[k].model()