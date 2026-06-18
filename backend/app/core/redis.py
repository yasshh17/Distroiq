import logging
from typing import Any
from urllib.parse import urlparse

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_pool: Redis | None = None


async def init_redis() -> Redis:
    global _redis_pool

    if _redis_pool is not None:
        return _redis_pool

    try:
        parsed = urlparse(settings.REDIS_URL)

        if parsed.scheme in ("rediss", "redis+tls"):
            _redis_pool = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                ssl_cert_reqs=None,
            )
        else:
            if parsed.scheme != "redis":
                logger.warning(f"Unknown Redis scheme: {parsed.scheme}, trying as-is")
            _redis_pool = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

        await _redis_pool.ping()
        logger.info(f"Connected to Redis at {parsed.hostname}")

        return _redis_pool

    except Exception as exc:
        logger.error(f"Failed to connect to Redis: {exc}")
        raise


async def get_redis() -> Redis:
    if _redis_pool is None:
        return await init_redis()
    return _redis_pool


async def close_redis() -> None:
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Disconnected from Redis")


class RedisCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        return await self.redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> bool:
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key) > 0

    async def get_json(self, key: str) -> dict[str, Any] | None:
        import json
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: dict[str, Any], ttl: int = 3600) -> bool:
        import json
        return await self.set(key, json.dumps(value), ttl)


async def get_cache() -> RedisCache:
    redis_client = await get_redis()
    return RedisCache(redis_client)