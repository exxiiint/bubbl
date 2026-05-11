from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import notifications as notifications_repo
from app.schemas.notification import NotificationPublic, NotificationsResponse
from app.services.users import serialize_compact


NOTIFICATION_TEXT = {
    "like": "оценил(а) вашу публикацию",
    "comment": "оставил(а) комментарий",
    "follow": "подписался(ась) на вас",
}


def create_notification(
    db: Session,
    user_id: UUID,
    notification_type: str,
    actor_id: UUID | None = None,
    post_id: UUID | None = None,
    comment_id: UUID | None = None,
) -> None:
    if actor_id is not None and actor_id == user_id:
        return
    notifications_repo.create(
        db,
        user_id=user_id,
        notification_type=notification_type,
        actor_id=actor_id,
        post_id=post_id,
        comment_id=comment_id,
    )


def list_notifications(db: Session, user_id: UUID, limit: int = 40, offset: int = 0) -> NotificationsResponse:
    rows = notifications_repo.list_for_user(db, user_id, limit=limit, offset=offset)
    items = [
        NotificationPublic(
            id=notification.id,
            type=notification.type,
            actor=serialize_compact(actor),
            post_id=notification.post_id,
            comment_id=notification.comment_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            text=NOTIFICATION_TEXT.get(notification.type, "создал(а) событие"),
        )
        for notification, actor in rows
    ]
    return NotificationsResponse(items=items, unread_count=notifications_repo.unread_count(db, user_id))


def mark_all_read(db: Session, user_id: UUID) -> NotificationsResponse:
    notifications_repo.mark_all_read(db, user_id)
    db.commit()
    return list_notifications(db, user_id)
