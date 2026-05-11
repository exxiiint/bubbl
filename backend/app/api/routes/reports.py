from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.report import ReportCreate, ReportPublic
from app.services import reports as reports_service

router = APIRouter(tags=["reports"])


@router.post("/posts/{post_id}/report", response_model=ReportPublic, summary="Пожаловаться на публикацию")
def create_report(post_id: UUID, payload: ReportCreate, db: DbSession, current_user: CurrentUser) -> ReportPublic:
    return reports_service.create_report(db, current_user, post_id, payload)


@router.get("/admin/reports", response_model=list[ReportPublic], summary="Жалобы для админ-панели")
def admin_reports(
    db: DbSession,
    current_user: CurrentUser,
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[ReportPublic]:
    return reports_service.list_reports(db, status=status, limit=limit, offset=offset)


@router.post("/admin/reports/{report_id}/reviewed", response_model=ReportPublic, summary="Отметить жалобу обработанной")
def mark_report_reviewed(report_id: UUID, db: DbSession, current_user: CurrentUser) -> ReportPublic:
    return reports_service.mark_report_reviewed(db, report_id)
