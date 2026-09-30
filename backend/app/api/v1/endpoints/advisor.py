"""
Advisor controller - personalized security tips.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.schemas.response import AdvisorMessageOut
from app.services.advisor_service import AdvisorService

router = APIRouter(tags=["Advisor"])


@router.get("/advisor", response_model=list[AdvisorMessageOut], summary="List my security tips")
def list_tips(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return AdvisorService(db).list(user)


@router.post("/advisor/{msg_id}/read", summary="Mark a tip as read")
def mark_read(msg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    AdvisorService(db).mark_read(user, msg_id)
    return {"message": "ok"}


@router.post("/advisor/read-all", summary="Mark all tips as read")
def mark_all_read(db: Session = Depends(get_db), user=Depends(get_current_user)):
    AdvisorService(db).mark_all_read(user)
    return {"message": "ok"}