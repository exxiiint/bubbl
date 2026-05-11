from __future__ import annotations

import mimetypes
import random
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.redis import invalidate_pattern
from app.core.security import hash_password
from app.core.storage import save_media_record, storage
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.like import Like
from app.models.notification import Notification
from app.models.post import Post
from app.models.report import Report
from app.models.user import User

DATASET = "pavansanagapati/images-dataset"
TARGET_USERS = 120
TARGET_POSTS = 1100
PASSWORD = "password123"

FIRST_NAMES = [
    "Аня", "Полина", "Филипп", "Сергей", "Мира", "Лена", "Тимур", "Варя", "Игорь", "Никита",
    "Кира", "Даша", "Марк", "Саша", "Алиса", "Егор", "Лиза", "Рома", "Маша", "Даня",
]
FIRST_NAME_SLUGS = [
    "anya", "polina", "filipp", "sergey", "mira", "lena", "timur", "varya", "igor", "nikita",
    "kira", "dasha", "mark", "sasha", "alisa", "egor", "liza", "roma", "masha", "danya",
]
LAST_BITS = ["photo", "glass", "city", "daily", "frame", "pixel", "soft", "light", "walk", "mood"]
HASHTAGS = [
    "#закат", "#улицы", "#город", "#фиолетовый", "#портрет", "#архитектура", "#кофе", "#путешествия",
    "#стекло", "#минимализм", "#природа", "#свет", "#друзья", "#лето", "#bubbl", "#фото", "#день",
]
CAPTIONS = [
    "Оставлю это здесь",
    "Сегодняшний кадр",
    "Поймал настроение",
    "Мягкий свет и хороший день",
    "Город снова удивляет",
    "Маленькая деталь, которую не хочется терять",
    "Цвет, воздух, движение",
    "Кажется, это попадёт в любимое",
]
COMMENTS = [
    "Очень красиво!",
    "Сохранил в референсы.",
    "Классный кадр.",
    "Атмосферно получилось.",
    "Цвета прям живые.",
    "Хороший момент.",
]
REPORT_REASONS = ["Спам", "Неуместный контент", "Оскорбления", "Нарушение правил", "Подозрительная публикация"]


def download_dataset() -> list[Path]:
    try:
        import kagglehub

        dataset_dir = Path(kagglehub.dataset_download(DATASET))
        print(f"Kaggle dataset: {dataset_dir}")
    except Exception as exc:
        print(f"Kaggle dataset недоступен, использую fallback SVG: {exc}")
        return []

    exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = [path for path in dataset_dir.rglob("*") if path.suffix.lower() in exts and path.is_file()]
    random.shuffle(images)
    print(f"Найдено изображений: {len(images)}")
    return images


def svg_image(title: str, seed: int) -> bytes:
    palettes = [
        ("#8b5cf6", "#f2ecff"),
        ("#14b8a6", "#ecfeff"),
        ("#ec4899", "#fff1f7"),
        ("#f59e0b", "#fff7ed"),
        ("#6366f1", "#eef2ff"),
    ]
    primary, background = palettes[seed % len(palettes)]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900">
  <rect width="1200" height="900" rx="80" fill="{background}"/>
  <circle cx="{220 + seed % 500}" cy="260" r="210" fill="{primary}" opacity="0.25"/>
  <circle cx="920" cy="{460 + seed % 260}" r="260" fill="#ffffff" opacity="0.45"/>
  <rect x="120" y="120" width="960" height="660" rx="64" fill="#ffffff" opacity="0.38"/>
  <text x="600" y="440" text-anchor="middle" font-size="74" font-family="Arial, sans-serif" font-weight="700" fill="#252238">{title}</text>
</svg>
""".strip().encode("utf-8")


def upload_image(db: Session, owner_id: UUID, images: list[Path], index: int, prefix: str, title: str):
    if images:
        image = images[index % len(images)]
        data = image.read_bytes()
        content_type = mimetypes.guess_type(image.name)[0] or "image/jpeg"
        suffix = image.suffix or ".jpg"
    else:
        data = svg_image(title, index)
        content_type = "image/svg+xml"
        suffix = ".svg"

    stored = storage.upload_bytes(data, owner_id=owner_id, content_type=content_type, prefix=prefix, suffix=suffix)
    save_media_record(db, owner_id, stored)
    return stored


def ensure_users(db: Session, images: list[Path]) -> list[User]:
    users = list(db.scalars(select(User).order_by(User.created_at.asc())).all())
    existing_usernames = {user.username for user in users}

    for index in range(len(users), TARGET_USERS):
        name = FIRST_NAMES[index % len(FIRST_NAMES)]
        slug = FIRST_NAME_SLUGS[index % len(FIRST_NAME_SLUGS)]
        username = f"{slug}_{LAST_BITS[index % len(LAST_BITS)]}_{index:03d}"
        while username in existing_usernames:
            username = f"{username}_{random.randint(10, 99)}"
        existing_usernames.add(username)

        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=hash_password(PASSWORD),
            display_name=f"{name} {index + 1}",
            bio=random.choice(
                [
                    "Собираю красивые кадры и спокойные моменты.",
                    "Фотографирую город, свет и детали.",
                    "Здесь мои прогулки, люди и настроение.",
                    "Люблю живые цвета и мягкие тени.",
                ]
            ),
        )
        db.add(user)
        db.flush()
        avatar = upload_image(db, user.id, images, index, "avatars", user.display_name)
        user.avatar_url = avatar.public_url
        user.avatar_object_key = avatar.object_key
        users.append(user)

        if index % 20 == 0:
            db.commit()
            print(f"Пользователей: {len(users)}")

    db.commit()
    return list(db.scalars(select(User).order_by(User.created_at.asc())).all())


def ensure_graph(db: Session, users: list[User]) -> None:
    existing = {(row.follower_id, row.following_id) for row in db.scalars(select(Follow)).all()}
    for user in users:
        candidates = [candidate for candidate in users if candidate.id != user.id]
        for target in random.sample(candidates, k=min(len(candidates), random.randint(8, 18))):
            pair = (user.id, target.id)
            if pair in existing:
                continue
            existing.add(pair)
            db.add(Follow(follower_id=user.id, following_id=target.id))
    db.commit()


def ensure_posts(db: Session, users: list[User], images: list[Path]) -> list[Post]:
    posts = list(db.scalars(select(Post).where(Post.deleted_at.is_(None)).order_by(Post.created_at.asc())).all())
    for index in range(len(posts), TARGET_POSTS):
        author = random.choice(users)
        tags = " ".join(random.sample(HASHTAGS, k=random.randint(2, 5)))
        caption = f"{random.choice(CAPTIONS)} {tags}"
        media = upload_image(db, author.id, images, index, "posts", f"Публикация {index + 1}")
        post = Post(author_id=author.id, caption=caption, media_url=media.public_url, media_object_key=media.object_key)
        db.add(post)
        db.flush()
        posts.append(post)

        if (index + 1) % 100 == 0:
            db.commit()
            print(f"Публикаций: {index + 1}")

    db.commit()
    return list(db.scalars(select(Post).where(Post.deleted_at.is_(None)).order_by(Post.created_at.asc())).all())


def enrich_activity(db: Session, users: list[User], posts: list[Post]) -> None:
    existing_likes = {(like.user_id, like.post_id) for like in db.scalars(select(Like)).all()}
    existing_comments = db.scalar(select(Comment.id).limit(1)) is not None

    for index, post in enumerate(random.sample(posts, k=min(len(posts), 850))):
        for user in random.sample(users, k=random.randint(5, 18)):
            if user.id == post.author_id or (user.id, post.id) in existing_likes:
                continue
            existing_likes.add((user.id, post.id))
            db.add(Like(user_id=user.id, post_id=post.id))
            if random.random() < 0.12:
                db.add(Notification(user_id=post.author_id, actor_id=user.id, type="like", post_id=post.id))

        if not existing_comments or random.random() < 0.72:
            for user in random.sample(users, k=random.randint(1, 4)):
                if user.id == post.author_id:
                    continue
                comment = Comment(user_id=user.id, post_id=post.id, text=random.choice(COMMENTS))
                db.add(comment)
                db.flush()
                if random.random() < 0.2:
                    db.add(Notification(user_id=post.author_id, actor_id=user.id, type="comment", post_id=post.id, comment_id=comment.id))

        if index % 80 == 0:
            db.commit()

    open_reports = [report for report in db.scalars(select(Report).where(Report.status == "open")).all()]
    reports_to_create = max(0, 25 - len(open_reports))
    if reports_to_create:
        reported_pairs = {(report.reporter_id, report.post_id) for report in open_reports}
        for post in random.sample(posts, k=min(reports_to_create, len(posts))):
            reporter = random.choice([user for user in users if user.id != post.author_id])
            if (reporter.id, post.id) in reported_pairs:
                continue
            reported_pairs.add((reporter.id, post.id))
            db.add(
                Report(
                    reporter_id=reporter.id,
                    post_id=post.id,
                    reason=random.choice(REPORT_REASONS),
                    details="Демо-жалоба для админ-панели.",
                )
            )

    db.commit()


def main() -> None:
    random.seed(20260511)
    storage.ensure_bucket()
    db = SessionLocal()
    try:
        images = download_dataset()
        users = ensure_users(db, images)
        ensure_graph(db, users)
        posts = ensure_posts(db, users, images)
        enrich_activity(db, users, posts)
        invalidate_pattern("feed:*")
        invalidate_pattern("trends:*")
        print(f"Heavy seed готов: пользователей {len(users)}, публикаций {len(posts)}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
