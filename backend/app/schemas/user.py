from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCompact(BaseModel):
    id: UUID
    username: str
    display_name: str
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserCompact):
    email: EmailStr | None = None
    bio: str | None = None
    created_at: datetime | None = None
    posts_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    is_following: bool = False


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=700)
