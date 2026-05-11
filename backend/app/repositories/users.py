from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.models.report import Report
from app.models.user import User


def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.get(User, user_id)


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.username) == username.lower()))


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.lower()))


def get_by_login(db: Session, login: str) -> User | None:
    normalized = login.lower()
    return db.scalar(select(User).where(or_(func.lower(User.email) == normalized, func.lower(User.username) == normalized)))


def create(db: Session, username: str, email: str, password_hash: str, display_name: str) -> User:
    user = User(username=username, email=email, password_hash=password_hash, display_name=display_name)
    db.add(user)
    db.flush()
    return user


def update_profile(
    db: Session,
    user: User,
    display_name: str | None = None,
    bio: str | None = None,
    avatar_url: str | None = None,
    avatar_object_key: str | None = None,
) -> User:
    if display_name is not None:
        user.display_name = display_name
    if bio is not None:
        user.bio = bio
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if avatar_object_key is not None:
        user.avatar_object_key = avatar_object_key
    db.add(user)
    db.flush()
    return user


def search(db: Session, query: str, limit: int = 20) -> list[User]:
    pattern = f"%{query.lower()}%"
    return list(
        db.scalars(
            select(User)
            .where(or_(func.lower(User.username).like(pattern), func.lower(User.display_name).like(pattern)))
            .order_by(User.username.asc())
            .limit(limit)
        )
    )


def count_posts(db: Session, user_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Post).where(Post.author_id == user_id, Post.deleted_at.is_(None))) or 0


def count_followers(db: Session, user_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Follow).where(Follow.following_id == user_id)) or 0


def count_following(db: Session, user_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)) or 0


def system_counts(db: Session) -> dict[str, int]:
    return {
        "users_count": db.scalar(select(func.count()).select_from(User)) or 0,
        "posts_count": db.scalar(select(func.count()).select_from(Post).where(Post.deleted_at.is_(None))) or 0,
        "likes_count": db.scalar(select(func.count()).select_from(Like)) or 0,
        "comments_count": db.scalar(select(func.count()).select_from(Comment).where(Comment.deleted_at.is_(None))) or 0,
        "reports_count": db.scalar(select(func.count()).select_from(Report).where(Report.status == "open")) or 0,
    }
