from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.comment import Comment


def create(db: Session, user_id: UUID, post_id: UUID, text: str) -> Comment:
    comment = Comment(user_id=user_id, post_id=post_id, text=text)
    db.add(comment)
    db.flush()
    return comment


def get(db: Session, comment_id: UUID) -> Comment | None:
    return db.get(Comment, comment_id)


def list_for_post(db: Session, post_id: UUID, limit: int = 50, offset: int = 0) -> list[Comment]:
    return list(
        db.scalars(
            select(Comment)
            .where(Comment.post_id == post_id, Comment.deleted_at.is_(None))
            .order_by(Comment.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
    )


def count_for_post(db: Session, post_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id == post_id, Comment.deleted_at.is_(None))) or 0


def soft_delete(db: Session, comment: Comment) -> Comment:
    comment.deleted_at = datetime.now(UTC)
    db.add(comment)
    db.flush()
    return comment
