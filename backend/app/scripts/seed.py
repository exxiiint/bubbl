from __future__ import annotations

import random
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.core.storage import save_media_record, storage
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.like import Like
from app.models.notification import Notification
from app.models.post import Post
from app.models.user import User

random.seed(42)

SEED_USERS = [
    ("filipp", "filipp@example.com", "Филипп", "Люблю архитектуру, хорошие интерфейсы и городские кадры."),
    ("anya", "anya@example.com", "Аня", "Собираю свет, фактуры и маленькие моменты."),
    ("polinakriv", "polina@example.com", "Полина", "Фотографирую прогулки и мягкие цвета."),
    ("sergey.jpg", "sergey@example.com", "Сергей", "Пиксели, кофе и аккуратные API."),
    ("mira", "mira@example.com", "Мира", "Дизайн-наблюдения и заметки из города."),
    ("nikita", "nikita@example.com", "Никита", "Backend, бег и вечернее небо."),
    ("lena.ui", "lena@example.com", "Лена", "UI, стекло, типографика."),
    ("timur", "timur@example.com", "Тимур", "Системы, графы и хорошие README."),
    ("varya", "varya@example.com", "Варя", "Снимаю детали, которые обычно пропускают."),
    ("igor.dev", "igor@example.com", "Игорь", "Смотрю на нагрузку и профили запросов."),
]

CAPTIONS = [
    "Мягкий свет на конце дня. #закат #свет",
    "Город сегодня выглядит особенно тихим. #город #улицы",
    "Фиолетовый акцент спас композицию. #фиолетовый #дизайн",
    "Поймал отражение в стекле. #улицы #стекло",
    "Красивый кадр для новой ленты. #bubbl #фото",
    "Система держится на хороших границах. #архитектура #backend",
    "Пост про то, как данные становятся историей. #данные #город",
    "Проверяем ленту на практике. #лента #архитектура",
]

HASHTAG_PAIRS = [
    "#закат #свет",
    "#улицы #город",
    "#фиолетовый #дизайн",
    "#стекло #фото",
    "#архитектура #backend",
    "#лента #bubbl",
]

COLORS = [
    ("#8b5cf6", "#f2ecff"),
    ("#6d28d9", "#ede7f7"),
    ("#ec4899", "#fff1f7"),
    ("#14b8a6", "#ecfeff"),
    ("#f59e0b", "#fff7ed"),
    ("#6366f1", "#eef2ff"),
]


def svg_image(title: str, primary: str, background: str) -> bytes:
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="{background}"/>
      <stop offset="100%" stop-color="{primary}" stop-opacity="0.55"/>
    </linearGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="48"/></filter>
  </defs>
  <rect width="1200" height="900" rx="80" fill="url(#g)"/>
  <circle cx="260" cy="220" r="180" fill="{primary}" opacity="0.24" filter="url(#blur)"/>
  <circle cx="930" cy="640" r="230" fill="#ffffff" opacity="0.38" filter="url(#blur)"/>
  <rect x="120" y="120" width="960" height="660" rx="64" fill="#ffffff" opacity="0.38"/>
  <text x="600" y="430" text-anchor="middle" font-size="74" font-family="Arial, sans-serif" font-weight="700" fill="#252238">{title}</text>
  <text x="600" y="505" text-anchor="middle" font-size="34" font-family="Arial, sans-serif" fill="#6f6a80">bubbl seed media</text>
</svg>
""".strip().encode("utf-8")


def avatar_svg(display_name: str, primary: str, background: str) -> bytes:
    initials = "".join(part[0] for part in display_name.split()[:2]).upper()
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
  <rect width="320" height="320" rx="120" fill="{background}"/>
  <circle cx="228" cy="92" r="88" fill="{primary}" opacity="0.38"/>
  <circle cx="100" cy="238" r="112" fill="{primary}" opacity="0.22"/>
  <text x="160" y="184" text-anchor="middle" font-size="92" font-family="Arial, sans-serif" font-weight="700" fill="#252238">{initials}</text>
</svg>
""".strip().encode("utf-8")


def put_seed_media(db: Session, owner_id: UUID, data: bytes, prefix: str, name: str):
    stored = storage.upload_bytes(data, owner_id=owner_id, content_type="image/svg+xml", prefix=prefix, suffix=".svg")
    save_media_record(db, owner_id, stored)
    return stored


def backfill_existing_seed(db: Session) -> None:
    changed = False
    users_by_username = {user.username: user for user in db.scalars(select(User)).all()}
    for username, email, display_name, bio in SEED_USERS:
        user = users_by_username.get(username)
        if user is None:
            continue
        if user.email != email:
            user.email = email
        if user.display_name != display_name:
            user.display_name = display_name
        if user.bio != bio:
            user.bio = bio
        changed = True

    posts = db.scalars(select(Post).where(Post.deleted_at.is_(None)).order_by(Post.created_at.asc())).all()
    for index, post in enumerate(posts):
        if post.caption and "#" in post.caption:
            continue
        base = (post.caption or random.choice(CAPTIONS)).strip()
        post.caption = f"{base} {HASHTAG_PAIRS[index % len(HASHTAG_PAIRS)]}"
        changed = True

    if changed:
        db.commit()
        print("Seed обновил тестовые профили и хештеги.")
    else:
        print("Seed уже применён: пользователь filipp существует.")


def main() -> None:
    storage.ensure_bucket()
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "filipp").first():
            backfill_existing_seed(db)
            return

        users: list[User] = []
        for index, (username, email, display_name, bio) in enumerate(SEED_USERS):
            primary, background = COLORS[index % len(COLORS)]
            user = User(
                username=username,
                email=email,
                password_hash=hash_password("password123"),
                display_name=display_name,
                bio=bio,
            )
            db.add(user)
            db.flush()
            avatar = put_seed_media(db, user.id, avatar_svg(display_name, primary, background), "avatars", username)
            user.avatar_url = avatar.public_url
            user.avatar_object_key = avatar.object_key
            users.append(user)

        for follower in users:
            candidates = [u for u in users if u.id != follower.id]
            for followed in random.sample(candidates, k=random.randint(3, 6)):
                db.add(Follow(follower_id=follower.id, following_id=followed.id))
        db.flush()

        posts: list[Post] = []
        for i in range(32):
            author = random.choice(users)
            primary, background = COLORS[i % len(COLORS)]
            stored = put_seed_media(db, author.id, svg_image(f"Публикация {i + 1}", primary, background), "posts", str(i))
            post = Post(
                author_id=author.id,
                caption=random.choice(CAPTIONS),
                media_url=stored.public_url,
                media_object_key=stored.object_key,
            )
            db.add(post)
            db.flush()
            posts.append(post)

        like_pairs: set[tuple[UUID, UUID]] = set()
        for post in posts:
            for user in random.sample(users, k=random.randint(2, 7)):
                if user.id == post.author_id or (user.id, post.id) in like_pairs:
                    continue
                like_pairs.add((user.id, post.id))
                db.add(Like(user_id=user.id, post_id=post.id))
                db.add(Notification(user_id=post.author_id, actor_id=user.id, type="like", post_id=post.id))

        comment_texts = [
            "Очень мягкий кадр!",
            "Композиция прям дышит.",
            "Сохранил(а) в референсы.",
            "Красиво и спокойно.",
            "Вот это стеклянное настроение.",
        ]
        for post in random.sample(posts, k=24):
            for user in random.sample(users, k=random.randint(1, 3)):
                if user.id == post.author_id:
                    continue
                comment = Comment(user_id=user.id, post_id=post.id, text=random.choice(comment_texts))
                db.add(comment)
                db.flush()
                db.add(Notification(user_id=post.author_id, actor_id=user.id, type="comment", post_id=post.id, comment_id=comment.id))

        db.commit()
        print("Seed готов. Тестовые пользователи: filipp, anya, polinakriv, sergey.jpg. Пароль: password123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
