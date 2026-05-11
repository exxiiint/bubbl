# API socialgram

Базовый URL: `http://localhost:8000/api`

## Auth

- `POST /auth/register` — регистрация.
- `POST /auth/login` — вход по email или username.
- `GET /auth/me` — текущий пользователь.

## Users

- `GET /users/me` — мой профиль.
- `PATCH /users/me` — редактирование display_name, bio, avatar.
- `GET /users/{username}` — публичный профиль.
- `GET /users/search?q=` — поиск.
- `POST /users/{user_id}/follow` — подписаться.
- `DELETE /users/{user_id}/follow` — отписаться.
- `GET /users/{user_id}/followers` — подписчики.
- `GET /users/{user_id}/following` — подписки.
- `GET /users/{user_id}/posts` — публикации пользователя.

## Posts и Feed

- `GET /feed` — главная лента.
- `POST /posts` — создать публикацию с изображением.
- `GET /posts/{post_id}` — открыть публикацию.
- `DELETE /posts/{post_id}` — мягко удалить свою публикацию.
- `POST /posts/{post_id}/report` — отправить жалобу на публикацию.
- `POST /posts/{post_id}/like` — поставить лайк.
- `DELETE /posts/{post_id}/like` — убрать лайк.
- `GET /posts/trends` — реальные хештеги по публикациям.

## Comments

- `POST /posts/{post_id}/comments` — добавить комментарий.
- `GET /posts/{post_id}/comments` — комментарии публикации.
- `DELETE /comments/{comment_id}` — удалить свой комментарий.

## Notifications

- `GET /notifications` — список уведомлений.
- `POST /notifications/read-all` — отметить все прочитанными.

## System

- `GET /health` — healthcheck.
- `GET /system/stats` — users_count, posts_count, likes_count, comments_count, reports_count.
- `GET /admin/reports` — открытые или все жалобы для админ-панели.
- `POST /admin/reports/{report_id}/reviewed` — отметить жалобу обработанной.

Полная интерактивная документация доступна в Swagger: `http://localhost:8000/docs`.
