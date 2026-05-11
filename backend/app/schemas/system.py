from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class SystemStats(BaseModel):
    users_count: int
    posts_count: int
    likes_count: int
    comments_count: int
    reports_count: int = 0
