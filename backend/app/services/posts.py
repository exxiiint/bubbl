import re
from collections import Counter
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.core.redis import cache_get_json, cache_set_json, invalidate_pattern
from app.core.storage import save_media_record, storage
from app.models.post import Post
from app.models.user import User
from app.repositories import comments as comments_repo
from app.repositories import likes as likes_repo
from app.repositories import posts as posts_repo
from app.repositories import users as users_repo
from app.schemas.post import FeedResponse, PostPublic, TrendPublic
from app.services.notifications import create_notification
from app.services.users import serialize_compact


def serialize_post(db: Session, post: Post, current_user_id: UUID | None = None) -> PostPublic:
    return PostPublic(
        id=post.id,
        author=serialize_compact(post.author) if post.author else serialize_compact(users_repo.get_by_id(db, post.author_id)),
        caption=post.caption,
        media_url=post.media_url,
        media_object_key=post.media_object_key,
        created_at=post.created_at,
        updated_at=post.updated_at,
        likes_count=likes_repo.count_for_post(db, post.id),
        comments_count=comments_repo.count_for_post(db, post.id),
        liked_by_me=likes_repo.liked_by_user(db, current_user_id, post.id),
    )


def create_post(db: Session, current_user: User, caption: str | None, image: UploadFile) -> PostPublic:
    if image.content_type and not image.content_type.startswith("image/"):
        raise ForbiddenError("Можно загружать только изображения")

    stored = storage.upload_file(image, current_user.id, "posts")
    save_media_record(db, current_user.id, stored)
    post = posts_repo.create(db, current_user.id, caption.strip() if caption else None, stored.public_url, stored.object_key)
    invalidate_pattern("feed:*")
    invalidate_pattern("trends:*")
    db.commit()
    post = posts_repo.get(db, post.id)
    return serialize_post(db, post, current_user.id)


def get_post(db: Session, post_id: UUID, current_user: User) -> PostPublic:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")
    return serialize_post(db, post, current_user.id)


def delete_post(db: Session, post_id: UUID, current_user: User) -> None:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")
    if post.author_id != current_user.id:
        raise ForbiddenError("Можно удалить только свою публикацию")
    posts_repo.soft_delete(db, post)
    invalidate_pattern("feed:*")
    invalidate_pattern("trends:*")
    db.commit()


def list_user_posts(db: Session, user_id: UUID, current_user: User, limit: int = 60, offset: int = 0) -> list[PostPublic]:
    if users_repo.get_by_id(db, user_id) is None:
        raise NotFoundError("Пользователь не найден")
    return [serialize_post(db, post, current_user.id) for post in posts_repo.list_by_user(db, user_id, limit=limit, offset=offset)]


def get_feed(db: Session, current_user: User, limit: int = 20, offset: int = 0) -> FeedResponse:
    cache_key = f"feed:{current_user.id}:{limit}:{offset}"
    cached = cache_get_json(cache_key)
    if cached:
        return FeedResponse.model_validate(cached)

    posts = posts_repo.feed(db, current_user.id, limit=limit, offset=offset)
    response = FeedResponse(
        items=[serialize_post(db, post, current_user.id) for post in posts],
        limit=limit,
        offset=offset,
        total=posts_repo.count_feed(db, current_user.id),
    )
    cache_set_json(cache_key, response.model_dump(mode="json"), ttl_seconds=45)
    return response


def get_trends(db: Session, limit: int = 6) -> list[TrendPublic]:
    cache_key = f"trends:{limit}"
    cached = cache_get_json(cache_key)
    if cached:
        return [TrendPublic.model_validate(item) for item in cached]

    counter: Counter[str] = Counter()
    for caption in posts_repo.list_active_captions(db):
        tags = {match.group(1).lower() for match in re.finditer(r"#([A-Za-zА-Яа-яЁё0-9_]{2,40})", caption or "")}
        counter.update(tags)

    trends = [TrendPublic(tag=f"#{tag}", posts_count=count) for tag, count in counter.most_common(limit)]
    cache_set_json(cache_key, [trend.model_dump(mode="json") for trend in trends], ttl_seconds=60)
    return trends


def like_post(db: Session, post_id: UUID, current_user: User) -> PostPublic:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")

    if likes_repo.get(db, current_user.id, post_id) is None:
        likes_repo.create(db, current_user.id, post_id)
        create_notification(db, user_id=post.author_id, notification_type="like", actor_id=current_user.id, post_id=post_id)
        invalidate_pattern("feed:*")
        db.commit()

    post = posts_repo.get(db, post_id)
    return serialize_post(db, post, current_user.id)


def unlike_post(db: Session, post_id: UUID, current_user: User) -> PostPublic:
    post = posts_repo.get(db, post_id)
    if post is None:
        raise NotFoundError("Публикация не найдена")
    like = likes_repo.get(db, current_user.id, post_id)
    if like is not None:
        likes_repo.delete(db, like)
        invalidate_pattern("feed:*")
        db.commit()
    post = posts_repo.get(db, post_id)
    return serialize_post(db, post, current_user.id)
