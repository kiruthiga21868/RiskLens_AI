"""
Report controller - CSV and PDF downloads.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.services.report_service import ReportService

router = APIRouter(tags=["Reports"])


@router.get("/reports/csv", summary="Download threat history as CSV")
def report_csv(db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = ReportService(db).build_csv(user)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return StreamingResponse(
        iter([data]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="risklens_report_{stamp}.csv"'},
    )


@router.get("/reports/pdf", summary="Download a PDF security report")
def report_pdf(db: Session = Depends(get_db), user=Depends(get_current_user)):
    data = ReportService(db).build_pdf(user)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="risklens_report_{stamp}.pdf"'},
    )