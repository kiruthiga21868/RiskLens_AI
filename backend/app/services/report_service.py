"""
ReportService - produces CSV and PDF security reports for a user.

CSV is trivial (csv module). PDF uses ReportLab to compose a branded
"Cyber Health Report" with the health score, threat summary and the most
recent assessments' recommendations. Returns bytes + a content type.
"""
import csv
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.user import User
from app.repositories.assessments_repository import AssessmentRepository, HealthRepository

BRAND = "#0f172a"
ACCENT = "#38bdf8"


class ReportService:
    def __init__(self, db) -> None:
        self.db = db
        self.assess_repo = AssessmentRepository(db)
        self.health_repo = HealthRepository(db)

    def build_csv(self, user: User) -> bytes:
        items = self.assess_repo.list_for_user(user.id, limit=200)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "type", "content", "prediction", "confidence",
                         "risk_score", "created_at", "recommendation"])
        for a in items:
            writer.writerow([a.id, a.type, a.content, a.prediction, a.confidence,
                             a.risk_score, a.created_at, a.recommendation])
        return buffer.getvalue().encode("utf-8-sig")

    def build_pdf(self, user: User) -> bytes:
        latest = self.health_repo.latest(user.id)
        items = self.assess_repo.list_for_user(user.id, limit=12)
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                title=f"RiskLens AI Report - {user.username}")
        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=22, textColor=colors.HexColor(BRAND))
        h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor(BRAND), spaceAfter=6)
        body = styles["BodyText"]

        story = [Paragraph(f"RiskLens AI - Security Report", h1),
                 Paragraph(f"User: {user.full_name or user.username} | {user.email}", body),
                 Spacer(1, 6)]
        if latest:
            story.append(Paragraph(f"Cyber Health Score: <b>{latest.health_score:.0f}/100</b>", h2))
            comps = latest.factors or {}
            rows = [[k, f"{v:.1f}"] for k, v in comps.items()]
            table = Table([["Component", "Score"]] + rows)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(ACCENT)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]))
            story.extend([table, Spacer(1, 10)])

        if items:
            story.append(Paragraph("Recent Threat Assessments", h2))
            for a in items:
                story.append(Paragraph(
                    f"<b>[{a.type.upper()}]</b> {a.prediction} - risk {a.risk_score:.0f} "
                    f"({a.created_at.date() if a.created_at else '-n/a'})", body))
                story.append(Paragraph(f"&nbsp;&nbsp;{a.explanation}", body))
                story.append(Spacer(1, 4))

        doc.build(story)
        return buffer.getvalue()