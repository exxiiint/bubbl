from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserCompact


class NotificationPublic(BaseModel):
    id: UUID
    type: str
    actor: UserCompact | None = None
    post_id: UUID | None = None
    comment_id: UUID | None = None
    is_read: bool
    created_at: datetime
    text: str


class NotificationsResponse(BaseModel):
    items: list[NotificationPublic]
    unread_count: int
