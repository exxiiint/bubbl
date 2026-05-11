import json
import logging
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def cache_get_json(key: str) -> Any | None:
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except Exception as exc:  # pragma: no cover - cache failures must not break API reads
        logger.warning("Redis get failed for %s: %s", key, exc)
        return None


def cache_set_json(key: str, value: Any, ttl_seconds: int = 60) -> None:
    try:
        redis_client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis set failed for %s: %s", key, exc)


def invalidate_pattern(pattern: str) -> None:
    try:
        keys = list(redis_client.scan_iter(match=pattern, count=100))
        if keys:
            redis_client.delete(*keys)
    except Exception as exc:  # pragma: no cover
        logger.warning("Redis invalidation failed for %s: %s", pattern, exc)
