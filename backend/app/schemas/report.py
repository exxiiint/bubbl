from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserCompact


class ReportCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=120)
    details: str | None = Field(default=None, max_length=700)


class ReportPublic(BaseModel):
    id: UUID
    post_id: UUID
    reporter: UserCompact
    reason: str
    details: str | None = None
    status: str
    created_at: datetime
    reviewed_at: datetime | None = None
    post_caption: str | None = None
    post_media_url: str | None = None
