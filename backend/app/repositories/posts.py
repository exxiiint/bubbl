from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session, joinedload

from app.models.follow import Follow
from app.models.post import Post


def create(db: Session, author_id: UUID, caption: str | None, media_url: str, media_object_key: str) -> Post:
    post = Post(author_id=author_id, caption=caption, media_url=media_url, media_object_key=media_object_key)
    db.add(post)
    db.flush()
    return post


def get(db: Session, post_id: UUID) -> Post | None:
    return db.scalar(select(Post).options(joinedload(Post.author)).where(Post.id == post_id, Post.deleted_at.is_(None)))


def list_by_user(db: Session, user_id: UUID, limit: int = 60, offset: int = 0) -> list[Post]:
    return list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.author_id == user_id, Post.deleted_at.is_(None))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def feed(db: Session, user_id: UUID, limit: int = 20, offset: int = 0) -> list[Post]:
    followed = select(Follow.following_id).where(Follow.follower_id == user_id).union(select(literal(user_id)))
    return list(
        db.scalars(
            select(Post)
            .options(joinedload(Post.author))
            .where(Post.deleted_at.is_(None), Post.author_id.in_(followed))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def count_feed(db: Session, user_id: UUID) -> int:
    followed = select(Follow.following_id).where(Follow.follower_id == user_id).union(select(literal(user_id)))
    return (
        db.scalar(
            select(func.count())
            .select_from(Post)
            .where(Post.deleted_at.is_(None), Post.author_id.in_(followed))
        )
        or 0
    )


def list_active_captions(db: Session, limit: int = 1000) -> list[str]:
    return list(
        db.scalars(
            select(Post.caption)
            .where(Post.deleted_at.is_(None), Post.caption.is_not(None))
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
    )


def soft_delete(db: Session, post: Post) -> Post:
    post.deleted_at = datetime.now(UTC)
    db.add(post)
    db.flush()
    return post
