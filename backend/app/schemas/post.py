from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserCompact


class PostPublic(BaseModel):
    id: UUID
    author: UserCompact
    caption: str | None = None
    media_url: str
    media_object_key: str
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    liked_by_me: bool = False

    model_config = ConfigDict(from_attributes=True)


class FeedResponse(BaseModel):
    items: list[PostPublic]
    limit: int
    offset: int
    total: int


class TrendPublic(BaseModel):
    tag: str
    posts_count: int
