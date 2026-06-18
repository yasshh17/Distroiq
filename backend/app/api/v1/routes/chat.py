import asyncio
import hashlib
import json
import logging
import uuid
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.redis import get_cache
from app.core.security import AuthError, extract_user_id, verify_jwt
from app.services.ai.chain import stream_chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_cache_key(message: str, user_id: str) -> str:
    content = f"chat:{message}:{user_id}"
    return f"chat_response:{hashlib.md5(content.encode()).hexdigest()}"


async def _stream_from_cache(cached_lines: list[str]) -> AsyncGenerator[str, None]:
    for line in cached_lines:
        yield line
        await asyncio.sleep(0.01)


async def _stream_and_cache(
    message: str, user_id: str, cache_key: str
) -> AsyncGenerator[str, None]:
    cached_lines = []
    cache = await get_cache()

    try:
        async for line in stream_chat(message, user_id):
            cached_lines.append(line)
            yield line

        await cache.set_json(cache_key, {"lines": cached_lines}, ttl=300)
        logger.info(f"Cached chat response with key: {cache_key[:20]}...")

    except Exception as exc:
        logger.error(f"Error during streaming/caching: {exc}")
        if cached_lines:
            await cache.set_json(cache_key, {"lines": cached_lines}, ttl=300)
        raise


def _require_user(authorization: str | None) -> uuid.UUID:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len("bearer "):].strip()

    logger.warning("Token received (first 50 chars): %s", token[:50])
    logger.warning("JWT secret (first 10 chars): %s", settings.SUPABASE_JWT_SECRET[:10])

    try:
        payload = verify_jwt(token)
        logger.warning("JWT decoded successfully, sub: %s", payload.get("sub"))
        return extract_user_id(payload)
    except AuthError as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/stream")
async def chat_stream(
    message: str,
    authorization: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    user_id = _require_user(authorization)
    user_id_str = str(user_id)

    cache_key = _generate_cache_key(message, user_id_str)
    cache = await get_cache()
    cached_response = await cache.get_json(cache_key)

    if cached_response and "lines" in cached_response:
        logger.info(f"Cache HIT for key: {cache_key[:20]}...")
        return StreamingResponse(
            _stream_from_cache(cached_response["lines"]),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "X-Cache-Status": "HIT",
            },
        )
    else:
        logger.info(f"Cache MISS for key: {cache_key[:20]}...")
        return StreamingResponse(
            _stream_and_cache(message, user_id_str, cache_key),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "X-Cache-Status": "MISS",
            },
        )


