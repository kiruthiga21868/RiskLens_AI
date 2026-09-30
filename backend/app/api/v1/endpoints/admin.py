"""
Admin controller - platform statistics and user management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.base import get_db
from app.schemas.response import UserAdminOut
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", summary="Platform statistics (admin)")
def stats(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return AdminService(db).stats()


@router.get("/users", response_model=list[UserAdminOut], summary="List users (admin)")
def users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return AdminService(db).users()