from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User


def create(
    db: Session,
    user_id: UUID,
    notification_type: str,
    actor_id: UUID | None = None,
    post_id: UUID | None = None,
    comment_id: UUID | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=notification_type,
        post_id=post_id,
        comment_id=comment_id,
    )
    db.add(notification)
    db.flush()
    return notification


def list_for_user(db: Session, user_id: UUID, limit: int = 40, offset: int = 0) -> list[tuple[Notification, User | None]]:
    return list(
        db.execute(
            select(Notification, User)
            .outerjoin(User, Notification.actor_id == User.id)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )


def unread_count(db: Session, user_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False))) or 0


def mark_all_read(db: Session, user_id: UUID) -> None:
    db.execute(update(Notification).where(Notification.user_id == user_id).values(is_read=True))
    db.flush()
