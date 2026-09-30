"""
Dashboard controller - health score overview + awareness update.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.schemas.dashboard import AwarenessUpdate, DashboardResponse
from app.services.advisor_service import AdvisorService
from app.services.dashboard_service import DashboardService
from app.services.health_score_service import HealthScoreService

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardResponse, summary="Full dashboard payload")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return DashboardService(db).dashboard(user)


@router.post("/awareness", summary="Update awareness score")
def update_awareness(data: AwarenessUpdate, db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    data.score = max(0, min(100, data.score))
    svc = HealthScoreService(db)
    result = svc.update_awareness(user, data.score)
    AdvisorService(db).generate_from_health(user)
    return {"health_score": result, "status": "updated",
            "awareness_score": user.awareness_score}