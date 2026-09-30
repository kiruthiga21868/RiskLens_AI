"""
Detection controllers - URL, email and credential scanners.

Each route authenticates the user, delegates to DetectionService, then
refreshes the user's Cyber Health Score snapshot and re-generates advisor
tips so the dashboard stays current after every scan.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.schemas.detection import (
    CredentialScanRequest,
    DetectionResponse,
    EmailScanRequest,
    UrlScanRequest,
)
from app.services.advisor_service import AdvisorService
from app.services.detection_service import DetectionService
from app.services.health_score_service import HealthScoreService

router = APIRouter(tags=["Detection"])


def _refresh_posture(db: Session, user) -> None:
    """Recompute health + regenerate advisor tips after a scan."""
    HealthScoreService(db).compute(user)
    AdvisorService(db).generate_from_health(user)


@router.post("/url", response_model=DetectionResponse, summary="Analyze a URL")
def scan_url(data: UrlScanRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = DetectionService(db)
    result = svc.run_and_persist(user, "url", data.url)
    _refresh_posture(db, user)
    return result


@router.post("/email", response_model=DetectionResponse, summary="Analyze an email / SMS")
def scan_email(data: EmailScanRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = DetectionService(db)
    result = svc.run_and_persist(user, "email", data.content)
    _refresh_posture(db, user)
    return result


@router.post("/credential", response_model=DetectionResponse, summary="Assess a password's risk")
def scan_credential(data: CredentialScanRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = DetectionService(db)
    result = svc.run_password(user, data.password)
    _refresh_posture(db, user)
    return result