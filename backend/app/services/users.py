from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.storage import save_media_record, storage
from app.models.user import User
from app.repositories import follows as follows_repo
from app.repositories import users as users_repo
from app.schemas.user import UserCompact, UserPublic


def serialize_user(db: Session, user: User, current_user_id: UUID | None = None, include_email: bool = False) -> UserPublic:
    return UserPublic(
        id=user.id,
        username=user.username,
        email=user.email if include_email else None,
        display_name=user.display_name,
        bio=user.bio,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        posts_count=users_repo.count_posts(db, user.id),
        followers_count=users_repo.count_followers(db, user.id),
        following_count=users_repo.count_following(db, user.id),
        is_following=follows_repo.is_following(db, current_user_id, user.id),
    )


def serialize_compact(user: User | None) -> UserCompact | None:
    if user is None:
        return None
    return UserCompact.model_validate(user)


def get_me(db: Session, user: User) -> UserPublic:
    return serialize_user(db, user, current_user_id=user.id, include_email=True)


def get_profile_by_username(db: Session, username: str, current_user_id: UUID) -> UserPublic:
    user = users_repo.get_by_username(db, username)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return serialize_user(db, user, current_user_id=current_user_id, include_email=user.id == current_user_id)


def search_users(db: Session, query: str, current_user_id: UUID, limit: int = 20) -> list[UserPublic]:
    if not query.strip():
        return []
    return [serialize_user(db, user, current_user_id=current_user_id) for user in users_repo.search(db, query.strip(), limit)]


def update_me(
    db: Session,
    user: User,
    display_name: str | None = None,
    bio: str | None = None,
    avatar: UploadFile | None = None,
) -> UserPublic:
    avatar_url = None
    avatar_object_key = None
    if avatar is not None:
        stored = storage.upload_file(avatar, user.id, "avatars")
        save_media_record(db, user.id, stored)
        avatar_url = stored.public_url
        avatar_object_key = stored.object_key

    users_repo.update_profile(
        db,
        user,
        display_name=display_name,
        bio=bio,
        avatar_url=avatar_url,
        avatar_object_key=avatar_object_key,
    )
    db.commit()
    db.refresh(user)
    return serialize_user(db, user, current_user_id=user.id, include_email=True)


def get_public_users(db: Session, users: list[User], current_user_id: UUID) -> list[UserPublic]:
    return [serialize_user(db, user, current_user_id=current_user_id) for user in users]
