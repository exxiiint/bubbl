import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, comments, feed, notifications, posts, reports, system, users
from app.core.config import settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler, validation_error_handler
from app.core.storage import safe_ensure_bucket

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="socialgram API",
        description="Учебный архитектурный прототип социальной сети bubbl.",
        version="1.0.0",
        openapi_tags=[
            {"name": "auth", "description": "Регистрация, вход и текущий пользователь"},
            {"name": "users", "description": "Профили, поиск и подписки"},
            {"name": "posts", "description": "Публикации, лента и лайки"},
            {"name": "comments", "description": "Комментарии"},
            {"name": "notifications", "description": "Уведомления"},
            {"name": "reports", "description": "Жалобы и админская модерация"},
            {"name": "system", "description": "Healthcheck и системная статистика"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    @app.on_event("startup")
    def on_startup() -> None:
        safe_ensure_bucket()
        logger.info("MinIO bucket is ready: %s", settings.minio_bucket)

    app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth")
    app.include_router(users.router, prefix=f"{settings.api_prefix}/users")
    app.include_router(feed.router, prefix=settings.api_prefix)
    app.include_router(posts.router, prefix=f"{settings.api_prefix}/posts")
    app.include_router(comments.router, prefix=settings.api_prefix)
    app.include_router(notifications.router, prefix=f"{settings.api_prefix}/notifications")
    app.include_router(reports.router, prefix=settings.api_prefix)
    app.include_router(system.router, prefix=settings.api_prefix)
    return app


app = create_app()
