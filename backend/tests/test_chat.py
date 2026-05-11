"""
Tests for the /api/v1/chat/stream SSE endpoint and the stream_chat generator.

Uses a minimal FastAPI app (no lifespan, no real DB).  Network calls to
Anthropic and Supabase are eliminated via unittest.mock patches so these
tests run fully offline.
"""

import json
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock, patch

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes.chat import router as chat_router
from app.api.v1.routes.health import router as health_router

# ── Helpers ───────────────────────────────────────────────────────────────────

_JWT_SECRET = "test-jwt-secret-must-be-at-least-32-chars!!"


def _make_token(user_id: str | None = None) -> str:
    """HS256 JWT signed with the test secret — takes the fallback path in verify_jwt."""
    payload = {"sub": user_id or str(uuid.uuid4())}
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def _parse_sse(body: str) -> list[dict]:
    """Parse an SSE response body into a list of decoded JSON event objects."""
    events: list[dict] = []
    for block in body.split("\n\n"):
        line = block.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: "):]))
    return events


# ── Mock stream generators ────────────────────────────────────────────────────


async def _simple_stream(_message: str, _user_id: str) -> AsyncGenerator[str, None]:
    yield f"data: {json.dumps({'type': 'delta', 'content': 'Hello'})}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


async def _bad_llm_astream(*_args, **_kwargs):
    """Raises immediately — simulates an LLM network failure."""
    # The unreachable yield is intentional: it makes this an async generator
    # so Python treats _bad_llm_astream as AsyncGenerator rather than a coroutine.
    if False:  # noqa: SIM210
        yield
    raise RuntimeError("LLM unavailable")


# ── Minimal test apps ─────────────────────────────────────────────────────────

_health_app = FastAPI()
_health_app.include_router(health_router, prefix="/api/v1")

_chat_app = FastAPI()
_chat_app.include_router(chat_router, prefix="/api/v1")

health_client = TestClient(_health_app)
chat_client = TestClient(_chat_app)


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_health_returns_200() -> None:
    resp = health_client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_chat_no_auth_returns_401() -> None:
    resp = chat_client.get("/api/v1/chat/stream", params={"message": "test"})
    assert resp.status_code == 401


def test_chat_bad_token_returns_401() -> None:
    resp = chat_client.get(
        "/api/v1/chat/stream",
        params={"message": "test"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_chat_valid_returns_sse_with_delta_and_done() -> None:
    token = _make_token()
    with patch("app.api.v1.routes.chat.stream_chat", new=_simple_stream):
        resp = chat_client.get(
            "/api/v1/chat/stream",
            params={"message": "what is low stock?"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    events = _parse_sse(resp.text)
    types = [e["type"] for e in events]
    assert "delta" in types
    assert types[-1] == "done"


async def test_stream_always_ends_with_done_on_llm_error() -> None:
    """stream_chat's finally block must yield done even when the LLM raises."""
    from app.services.ai.chain import stream_chat

    mock_llm = MagicMock()
    mock_llm.astream = _bad_llm_astream

    with patch("app.services.ai.chain._llm", new=mock_llm):
        collected: list[str] = []
        async for chunk in stream_chat("test query", str(uuid.uuid4())):
            collected.append(chunk)

    assert collected, "stream_chat yielded nothing"
    events = _parse_sse("".join(collected))
    assert events[-1]["type"] == "done"
