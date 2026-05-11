from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.core.redis import invalidate_pattern
from app.models.user import User
from app.repositories import comments as comments_repo
from app.repositories import posts as posts_repo
from app.repositories import users as users_repo
from app.schemas.comment import CommentCreate, CommentPublic
from app.services.notifications import create_notification
from app.services.users import serialize_compact


def serialize_comment(db: Session, comment) -> CommentPublic:
    return CommentPublic(
        id=comment.id,
        user=serialize_compact(users_repo.get_by_id(db, comment.user_id)),
        post_id=comment.post_id,
        text=comment.text,
        created_at=comment.created_at,
    )


def add_comment(db: Session, post_id: UUID, current_user: User, payload: CommentCreate) -> CommentPublic:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")
    comment = comments_repo.create(db, current_user.id, post_id, payload.text.strip())
    create_notification(
        db,
        user_id=post.author_id,
        notification_type="comment",
        actor_id=current_user.id,
        post_id=post_id,
        comment_id=comment.id,
    )
    invalidate_pattern("feed:*")
    db.commit()
    return serialize_comment(db, comment)


def list_comments(db: Session, post_id: UUID, limit: int = 50, offset: int = 0) -> list[CommentPublic]:
    if posts_repo.get(db, post_id) is None:
        raise NotFoundError("Публикация не найдена")
    return [serialize_comment(db, comment) for comment in comments_repo.list_for_post(db, post_id, limit, offset)]


def delete_comment(db: Session, comment_id: UUID, current_user: User) -> None:
    comment = comments_repo.get(db, comment_id)
    if comment is None or comment.deleted_at is not None:
        raise NotFoundError("Комментарий не найден")
    if comment.user_id != current_user.id:
        raise ForbiddenError("Можно удалить только свой комментарий")
    comments_repo.soft_delete(db, comment)
    invalidate_pattern("feed:*")
    db.commit()
