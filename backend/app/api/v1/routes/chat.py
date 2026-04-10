"""
Chat endpoints.

  GET /api/v1/chat/stream  — SSE streaming response from Claude

Day 2: no RAG, no DB persistence.
Day 3 will add: conversation history, pgvector retrieval, message storage.
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.security import AuthError, extract_user_id, verify_jwt
from app.services.ai.chain import stream_chat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


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
    Start a streaming chat response.

    Returns a Server-Sent Events stream.  Each event is a JSON object:

        data: {"type": "delta", "content": "token text"}
        data: {"type": "done"}
        data: {"type": "error", "message": "error text"}
    """
    user_id = _require_user(authorization)

    return StreamingResponse(
        stream_chat(message, str(user_id)),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx/proxy buffering
            "Connection": "keep-alive",
        },
    )
