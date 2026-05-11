from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.comment import CommentCreate, CommentPublic
from app.services import comments as comments_service

router = APIRouter(tags=["comments"])


@router.post("/posts/{post_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED, summary="Добавить комментарий")
def add_comment(post_id: UUID, payload: CommentCreate, db: DbSession, current_user: CurrentUser) -> CommentPublic:
    return comments_service.add_comment(db, post_id, current_user, payload)


@router.get("/posts/{post_id}/comments", response_model=list[CommentPublic], summary="Комментарии публикации")
def list_comments(
    post_id: UUID,
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[CommentPublic]:
    return comments_service.list_comments(db, post_id, limit=limit, offset=offset)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить свой комментарий")
def delete_comment(comment_id: UUID, db: DbSession, current_user: CurrentUser) -> Response:
    comments_service.delete_comment(db, comment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
