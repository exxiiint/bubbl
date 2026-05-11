from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.user import User
from app.repositories import posts as posts_repo
from app.repositories import reports as reports_repo
from app.schemas.report import ReportCreate, ReportPublic
from app.services.users import serialize_compact


def serialize_report(report, reporter, post) -> ReportPublic:
    return ReportPublic(
        id=report.id,
        post_id=report.post_id,
        reporter=serialize_compact(reporter),
        reason=report.reason,
        details=report.details,
        status=report.status,
        created_at=report.created_at,
        reviewed_at=report.reviewed_at,
        post_caption=post.caption,
        post_media_url=post.media_url,
    )


def create_report(db: Session, current_user: User, post_id: UUID, payload: ReportCreate) -> ReportPublic:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")
    report = reports_repo.create(db, current_user.id, post_id, payload.reason.strip(), payload.details.strip() if payload.details else None)
    db.commit()
    return serialize_report(report, current_user, post)


def list_reports(db: Session, status: str | None = None, limit: int = 50, offset: int = 0) -> list[ReportPublic]:
    return [serialize_report(report, reporter, post) for report, reporter, post in reports_repo.list_reports(db, status, limit, offset)]


def mark_report_reviewed(db: Session, report_id: UUID) -> ReportPublic:
    report = reports_repo.get(db, report_id)
    if report is None:
        raise NotFoundError("Жалоба не найдена")
    reports_repo.mark_reviewed(db, report)
    db.commit()
    rows = reports_repo.list_reports(db, limit=1_000)
    for item in rows:
        if item[0].id == report_id:
            return serialize_report(*item)
    raise NotFoundError("Жалоба не найдена")
