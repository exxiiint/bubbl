import logging

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import users as users_repo
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.users import serialize_user

logger = logging.getLogger(__name__)


def register(db: Session, payload: RegisterRequest) -> TokenResponse:
    username = payload.username.strip().lower()
    email = payload.email.lower()

    if users_repo.get_by_username(db, username):
        raise ConflictError("Username уже занят")
    if users_repo.get_by_email(db, email):
        raise ConflictError("Email уже зарегистрирован")

    user = users_repo.create(
        db,
        username=username,
        email=email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
    )
    db.commit()
    db.refresh(user)
    logger.info("User registered: %s", user.username)
    return TokenResponse(access_token=create_access_token(user.id), user=serialize_user(db, user, user.id, include_email=True))


def login(db: Session, payload: LoginRequest) -> TokenResponse:
    user = users_repo.get_by_login(db, payload.login.strip())
    if user is None or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedError("Неверный логин или пароль")

    logger.info("User logged in: %s", user.username)
    return TokenResponse(access_token=create_access_token(user.id), user=serialize_user(db, user, user.id, include_email=True))
