from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.like import Like


def get(db: Session, user_id: UUID, post_id: UUID) -> Like | None:
    return db.scalar(select(Like).where(Like.user_id == user_id, Like.post_id == post_id))


def create(db: Session, user_id: UUID, post_id: UUID) -> Like:
    like = Like(user_id=user_id, post_id=post_id)
    db.add(like)
    db.flush()
    return like


def delete(db: Session, like: Like) -> None:
    db.delete(like)
    db.flush()


def count_for_post(db: Session, post_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Like).where(Like.post_id == post_id)) or 0


def liked_by_user(db: Session, user_id: UUID | None, post_id: UUID) -> bool:
    if user_id is None:
        return False
    return get(db, user_id, post_id) is not None
