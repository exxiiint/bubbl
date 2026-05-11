from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import AppError, NotFoundError
from app.core.redis import invalidate_pattern
from app.models.user import User
from app.repositories import follows as follows_repo
from app.repositories import users as users_repo
from app.services.notifications import create_notification
from app.services.users import get_public_users, serialize_user


def follow_user(db: Session, current_user: User, target_user_id: UUID):
    if current_user.id == target_user_id:
        raise AppError("Нельзя подписаться на самого себя")

    target = users_repo.get_by_id(db, target_user_id)
    if target is None:
        raise NotFoundError("Пользователь не найден")

    existing = follows_repo.get(db, current_user.id, target_user_id)
    if existing is None:
        follows_repo.create(db, current_user.id, target_user_id)
        create_notification(db, user_id=target_user_id, notification_type="follow", actor_id=current_user.id)
        invalidate_pattern(f"feed:{current_user.id}:*")
        db.commit()

    return serialize_user(db, target, current_user_id=current_user.id)


def unfollow_user(db: Session, current_user: User, target_user_id: UUID):
    target = users_repo.get_by_id(db, target_user_id)
    if target is None:
        raise NotFoundError("Пользователь не найден")

    existing = follows_repo.get(db, current_user.id, target_user_id)
    if existing is not None:
        follows_repo.delete(db, existing)
        invalidate_pattern(f"feed:{current_user.id}:*")
        db.commit()

    return serialize_user(db, target, current_user_id=current_user.id)


def list_followers(db: Session, current_user: User, user_id: UUID):
    if users_repo.get_by_id(db, user_id) is None:
        raise NotFoundError("Пользователь не найден")
    return get_public_users(db, follows_repo.followers(db, user_id), current_user.id)


def list_following(db: Session, current_user: User, user_id: UUID):
    if users_repo.get_by_id(db, user_id) is None:
        raise NotFoundError("Пользователь не найден")
    return get_public_users(db, follows_repo.following(db, user_id), current_user.id)
