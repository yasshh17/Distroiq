"""
Chat endpoints — placeholder.

Will be implemented when the LangChain RAG pipeline is wired up.

Planned endpoints:
  POST   /chat                → non-streaming response
  GET    /chat/stream         → SSE streaming response
  GET    /chat/conversations  → list user's conversations
  GET    /chat/conversations/{id}/messages  → fetch history
  DELETE /chat/conversations/{id}          → delete conversation
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])
