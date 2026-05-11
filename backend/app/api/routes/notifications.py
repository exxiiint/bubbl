from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.notification import NotificationsResponse
from app.services import notifications as notifications_service

router = APIRouter(tags=["notifications"])


@router.get("", response_model=NotificationsResponse, summary="Список уведомлений")
def notifications(db: DbSession, current_user: CurrentUser) -> NotificationsResponse:
    return notifications_service.list_notifications(db, current_user.id)


@router.post("/read-all", response_model=NotificationsResponse, summary="Отметить все уведомления прочитанными")
def read_all(db: DbSession, current_user: CurrentUser) -> NotificationsResponse:
    return notifications_service.mark_all_read(db, current_user.id)
