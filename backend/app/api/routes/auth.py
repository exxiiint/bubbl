from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.services import auth as auth_service
from app.services.users import get_me

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse, summary="Регистрация пользователя")
def register(payload: RegisterRequest, db: DbSession) -> TokenResponse:
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenResponse, summary="Вход по email или username")
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return auth_service.login(db, payload)


@router.get("/me", response_model=UserPublic, summary="Текущий пользователь")
def me(db: DbSession, current_user: CurrentUser) -> UserPublic:
    return get_me(db, current_user)
