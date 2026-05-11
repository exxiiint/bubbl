from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.user import User


def get(db: Session, follower_id: UUID, following_id: UUID) -> Follow | None:
    return db.get(Follow, {"follower_id": follower_id, "following_id": following_id})


def is_following(db: Session, follower_id: UUID | None, following_id: UUID) -> bool:
    if follower_id is None:
        return False
    return get(db, follower_id, following_id) is not None


def create(db: Session, follower_id: UUID, following_id: UUID) -> Follow:
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)
    db.flush()
    return follow


def delete(db: Session, follow: Follow) -> None:
    db.delete(follow)
    db.flush()


def followers(db: Session, user_id: UUID) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.following_id == user_id)
            .order_by(Follow.created_at.desc())
        )
    )


def following(db: Session, user_id: UUID) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .join(Follow, Follow.following_id == User.id)
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc())
        )
    )


def following_ids(db: Session, user_id: UUID) -> list[UUID]:
    return list(db.scalars(select(Follow.following_id).where(Follow.follower_id == user_id)))
