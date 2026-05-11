from fastapi import APIRouter

from app.api.deps import DbSession
from app.repositories import users as users_repo
from app.schemas.system import HealthResponse, SystemStats

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, summary="Healthcheck")
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="socialgram-backend")


@router.get("/system/stats", response_model=SystemStats, summary="Системная статистика")
def stats(db: DbSession) -> SystemStats:
    return SystemStats(**users_repo.system_counts(db))
