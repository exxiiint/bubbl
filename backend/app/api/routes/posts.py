from uuid import UUID

from fastapi import APIRouter, File, Form, Query, Response, UploadFile, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.post import FeedResponse, PostPublic, TrendPublic
from app.services import posts as posts_service

router = APIRouter(tags=["posts"])


@router.get("/feed", response_model=FeedResponse, summary="Лента текущего пользователя")
def feed(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
) -> FeedResponse:
    return posts_service.get_feed(db, current_user, limit=limit, offset=offset)


@router.post("", response_model=PostPublic, status_code=status.HTTP_201_CREATED, summary="Создать публикацию")
def create_post(
    db: DbSession,
    current_user: CurrentUser,
    caption: str | None = Form(default=None),
    image: UploadFile = File(...),
) -> PostPublic:
    return posts_service.create_post(db, current_user, caption, image)


@router.get("/trends", response_model=list[TrendPublic], summary="Актуальные хештеги")
def trends(db: DbSession, current_user: CurrentUser, limit: int = Query(default=6, ge=1, le=12)) -> list[TrendPublic]:
    return posts_service.get_trends(db, limit=limit)


@router.get("/{post_id}", response_model=PostPublic, summary="Просмотр публикации")
def get_post(post_id: UUID, db: DbSession, current_user: CurrentUser) -> PostPublic:
    return posts_service.get_post(db, post_id, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить свою публикацию")
def delete_post(post_id: UUID, db: DbSession, current_user: CurrentUser) -> Response:
    posts_service.delete_post(db, post_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/like", response_model=PostPublic, summary="Поставить лайк")
def like(post_id: UUID, db: DbSession, current_user: CurrentUser) -> PostPublic:
    return posts_service.like_post(db, post_id, current_user)


@router.delete("/{post_id}/like", response_model=PostPublic, summary="Убрать лайк")
def unlike(post_id: UUID, db: DbSession, current_user: CurrentUser) -> PostPublic:
    return posts_service.unlike_post(db, post_id, current_user)
