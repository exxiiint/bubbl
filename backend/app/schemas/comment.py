from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserCompact


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=700)


class CommentPublic(BaseModel):
    id: UUID
    user: UserCompact
    post_id: UUID
    text: str
    created_at: datetime
