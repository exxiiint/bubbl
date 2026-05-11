from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.report import Report
from app.models.user import User


def create(db: Session, reporter_id: UUID, post_id: UUID, reason: str, details: str | None = None) -> Report:
    report = Report(reporter_id=reporter_id, post_id=post_id, reason=reason, details=details)
    db.add(report)
    db.flush()
    return report


def get(db: Session, report_id: UUID) -> Report | None:
    return db.get(Report, report_id)


def list_reports(db: Session, status: str | None = None, limit: int = 50, offset: int = 0) -> list[tuple[Report, User, Post]]:
    statement = select(Report, User, Post).join(User, Report.reporter_id == User.id).join(Post, Report.post_id == Post.id)
    if status:
        statement = statement.where(Report.status == status)
    return list(db.execute(statement.order_by(Report.created_at.desc()).limit(limit).offset(offset)).all())


def count_open(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Report).where(Report.status == "open")) or 0


def mark_reviewed(db: Session, report: Report) -> Report:
    report.status = "reviewed"
    report.reviewed_at = datetime.now(UTC)
    db.add(report)
    db.flush()
    return report
