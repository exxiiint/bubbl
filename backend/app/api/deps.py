from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import users as users_repo

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Требуется авторизация")
    try:
        user_id = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError("Недействительный токен") from exc
    user = users_repo.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("Пользователь не найден")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]
