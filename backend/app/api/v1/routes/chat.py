"""
Chat endpoints.

  GET /api/v1/chat/stream  — SSE streaming response from Claude

Day 2: no RAG, no DB persistence.
Day 3 will add: conversation history, pgvector retrieval, message storage.
"""

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


# ── Cache helpers ─────────────────────────────────────────────────────

def _generate_cache_key(message: str, user_id: str) -> str:
    """Generate a cache key from message and user_id."""
    # Create a deterministic cache key from message content
    # Include user_id to isolate cache per user if needed
    content = f"chat:{message}:{user_id}"
    return f"chat_response:{hashlib.md5(content.encode()).hexdigest()}"


async def _stream_from_cache(cached_lines: list[str]) -> AsyncGenerator[str, None]:
    """Stream cached response lines to simulate real-time streaming."""
    for line in cached_lines:
        yield line
        # Add small delay between chunks to simulate streaming
        await asyncio.sleep(0.01)


async def _stream_and_cache(
    message: str, user_id: str, cache_key: str
) -> AsyncGenerator[str, None]:
    """Stream chat response and cache the complete result."""
    cached_lines = []
    cache = await get_cache()

    try:
        # Stream the response and collect lines for caching
        async for line in stream_chat(message, user_id):
            cached_lines.append(line)
            yield line

        # Cache the complete response with 300 second TTL
        await cache.set_json(cache_key, {"lines": cached_lines}, ttl=300)
        logger.info(f"Cached chat response with key: {cache_key[:20]}...")

    except Exception as exc:
        logger.error(f"Error during streaming/caching: {exc}")
        # Still try to cache partial response if we got some lines
        if cached_lines:
            await cache.set_json(cache_key, {"lines": cached_lines}, ttl=300)
        raise


# ── Auth helper ───────────────────────────────────────────────────────
# Lightweight JWT-only check — no DB lookup required until Day 3 when
# we need to persist messages against a real user row.

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


# ── Endpoint ──────────────────────────────────────────────────────────

@router.get("/stream")
async def chat_stream(
    message: str,
    authorization: Annotated[str | None, Header()] = None,
) -> StreamingResponse:
    """
    Start a streaming chat response with Redis caching.

    Returns a Server-Sent Events stream.  Each event is a JSON object:

        data: {"type": "delta", "content": "token text"}
        data: {"type": "done"}
        data: {"type": "error", "message": "error text"}

    Responses are cached for 300 seconds. Identical requests will be served
    from cache for faster response times.
    """
    user_id = _require_user(authorization)
    user_id_str = str(user_id)

    # Generate cache key from message content
    cache_key = _generate_cache_key(message, user_id_str)
    cache = await get_cache()

    # Check cache first
    cached_response = await cache.get_json(cache_key)

    if cached_response and "lines" in cached_response:
        # Cache hit - stream from cached response
        logger.info(f"Cache HIT for key: {cache_key[:20]}... (serving from cache)")

        return StreamingResponse(
            _stream_from_cache(cached_response["lines"]),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "X-Cache-Status": "HIT",  # Debug header
            },
        )
    else:
        # Cache miss - stream normally and cache the result
        logger.info(f"Cache MISS for key: {cache_key[:20]}... (generating response)")

        return StreamingResponse(
            _stream_and_cache(message, user_id_str, cache_key),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive",
                "X-Cache-Status": "MISS",  # Debug header
            },
        )


