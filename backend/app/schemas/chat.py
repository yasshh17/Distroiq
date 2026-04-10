"""
Pydantic v2 schemas for the chat domain.

Naming convention:
  *Create  — inbound payloads (request bodies)
  *Read    — outbound payloads (response bodies, from_attributes=True)
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Message ───────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class MessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Conversation ──────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=500)


class ConversationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationRead):
    messages: list[MessageRead] = []


# ── Chat request / response ───────────────────────────────────────────

class ChatRequest(BaseModel):
    """Payload sent by the frontend to start or continue a conversation."""

    message: str = Field(min_length=1, max_length=8_000)
    conversation_id: uuid.UUID | None = None


class ResponseComponent(BaseModel):
    """
    A rich UI component included in the AI response.
    The `type` field drives rendering in the frontend.
    """

    type: Literal["table", "alert", "email", "citation"]
    data: dict[str, Any]


class ChatResponse(BaseModel):
    """Returned by POST /chat (non-streaming)."""

    conversation_id: uuid.UUID
    message: MessageRead
    components: list[ResponseComponent] = []


# ── SSE stream events ─────────────────────────────────────────────────

class StreamDelta(BaseModel):
    type: Literal["delta"] = "delta"
    token: str


class StreamComponent(BaseModel):
    type: Literal["component"] = "component"
    component: ResponseComponent


class StreamDone(BaseModel):
    type: Literal["done"] = "done"
    conversation_id: uuid.UUID
    message_id: uuid.UUID


class StreamError(BaseModel):
    type: Literal["error"] = "error"
    detail: str
