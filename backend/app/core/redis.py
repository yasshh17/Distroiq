"""Redis connection and utilities for DistroIQ."""

import logging
from typing import Any
from urllib.parse import urlparse

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection pool
_redis_pool: Redis | None = None


async def init_redis() -> Redis:
    """Initialize Redis connection pool."""
    global _redis_pool

    if _redis_pool is not None:
        return _redis_pool

    try:
        # Parse Redis URL to determine connection method
        parsed = urlparse(settings.REDIS_URL)

        if parsed.scheme in ("rediss", "redis+tls"):
            # TLS Redis (Upstash with SSL)
            _redis_pool = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                ssl_cert_reqs=None,  # Required for some cloud Redis providers
            )
        elif parsed.scheme == "redis":
            # Standard Redis URL (redis://user:pass@host:port)
            _redis_pool = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        else:
            # Fallback - try as-is
            logger.warning(f"Unknown Redis scheme: {parsed.scheme}, trying as-is")
            _redis_pool = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

        # Test connection
        await _redis_pool.ping()
        logger.info(f"Connected to Redis at {parsed.hostname}")

        return _redis_pool

    except Exception as exc:
        logger.error(f"Failed to connect to Redis: {exc}")
        raise


async def get_redis() -> Redis:
    """Get the Redis connection pool."""
    if _redis_pool is None:
        return await init_redis()
    return _redis_pool


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Disconnected from Redis")


# ── Cache utilities ──────────────────────────────────────────────────

class RedisCache:
    """Redis-backed cache utilities."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> str | None:
        """Get a value from cache."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL in seconds."""
        return await self.redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        return await self.redis.exists(key) > 0

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """Get and parse JSON from cache."""
        import json
        value = await self.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: dict[str, Any], ttl: int = 3600) -> bool:
        """Serialize and set JSON in cache."""
        import json
        return await self.set(key, json.dumps(value), ttl)


async def get_cache() -> RedisCache:
    """Get a RedisCache instance."""
    redis_client = await get_redis()
    return RedisCache(redis_client)