"""
RAG pipeline — placeholder.

Will be implemented in the RAG pipeline prompt.

Pipeline steps (all async):
  1. embed(query)          → vector via Anthropic embeddings
  2. retrieve(vector, k)   → top-k chunks from pgvector
  3. augment(query, chunks) → formatted prompt with source context
  4. generate(prompt)      → stream tokens from Claude via LangChain

Each chunk in the retrieval result carries a `source` tag so the
frontend can render accurate SourceCitation components.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator


async def stream_rag_response(
    query: str,
    conversation_history: list[dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    Placeholder async generator.
    Will yield SSE-formatted JSON strings: delta / component / done / error.
    """
    raise NotImplementedError("RAG pipeline not yet implemented")
    yield  # make this a generator
