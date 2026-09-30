"""
Threat history controller - past scans, paginated.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.schemas.response import HistoryPage
from app.services.threat_service import ThreatService

router = APIRouter(tags=["Threats"])


@router.get("/threats", response_model=HistoryPage, summary="Paginated threat history")
def history(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
            db: Session = Depends(get_db), user=Depends(get_current_user)):
    return ThreatService(db).history(user, page, page_size)


@router.get("/threats/{threat_id}", summary="Single threat detail")
def threat_detail(threat_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return ThreatService(db).detail(user, threat_id)