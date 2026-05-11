from uuid import UUID

from fastapi import APIRouter, File, Form, Query, UploadFile

from app.api.deps import CurrentUser, DbSession
from app.schemas.post import PostPublic
from app.schemas.user import UserPublic
from app.services import follows as follows_service
from app.services import posts as posts_service
from app.services import users as users_service

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserPublic, summary="Мой профиль")
def get_me(db: DbSession, current_user: CurrentUser) -> UserPublic:
    return users_service.get_me(db, current_user)


@router.patch("/me", response_model=UserPublic, summary="Редактировать мой профиль")
def patch_me(
    db: DbSession,
    current_user: CurrentUser,
    display_name: str | None = Form(default=None),
    bio: str | None = Form(default=None),
    avatar: UploadFile | None = File(default=None),
) -> UserPublic:
    return users_service.update_me(db, current_user, display_name=display_name, bio=bio, avatar=avatar)


@router.get("/search", response_model=list[UserPublic], summary="Поиск пользователей")
def search_users(
    db: DbSession,
    current_user: CurrentUser,
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[UserPublic]:
    return users_service.search_users(db, q, current_user.id, limit)


@router.post("/{user_id}/follow", response_model=UserPublic, summary="Подписаться")
def follow(user_id: UUID, db: DbSession, current_user: CurrentUser) -> UserPublic:
    return follows_service.follow_user(db, current_user, user_id)


@router.delete("/{user_id}/follow", response_model=UserPublic, summary="Отписаться")
def unfollow(user_id: UUID, db: DbSession, current_user: CurrentUser) -> UserPublic:
    return follows_service.unfollow_user(db, current_user, user_id)


@router.get("/{user_id}/followers", response_model=list[UserPublic], summary="Подписчики пользователя")
def followers(user_id: UUID, db: DbSession, current_user: CurrentUser) -> list[UserPublic]:
    return follows_service.list_followers(db, current_user, user_id)


@router.get("/{user_id}/following", response_model=list[UserPublic], summary="Подписки пользователя")
def following(user_id: UUID, db: DbSession, current_user: CurrentUser) -> list[UserPublic]:
    return follows_service.list_following(db, current_user, user_id)


@router.get("/{user_id}/posts", response_model=list[PostPublic], summary="Публикации пользователя")
def user_posts(
    user_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(default=60, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[PostPublic]:
    return posts_service.list_user_posts(db, user_id, current_user, limit=limit, offset=offset)


@router.get("/{username}", response_model=UserPublic, summary="Профиль по username")
def profile(username: str, db: DbSession, current_user: CurrentUser) -> UserPublic:
    return users_service.get_profile_by_username(db, username, current_user.id)
