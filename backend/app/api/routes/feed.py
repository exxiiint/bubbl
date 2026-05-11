from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.post import FeedResponse
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
