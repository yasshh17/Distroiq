"""
LangChain streaming chain — Day 2 (no RAG, no persistence).

Exposes a single coroutine:

    stream_chat(message, user_id) -> AsyncGenerator[str, None]

Each yielded string is a complete SSE line ready to be forwarded to
the browser:

    data: {"type": "delta", "content": "token text"}\n\n
    data: {"type": "done"}\n\n
    data: {"type": "error", "message": "..."}\n\n

RAG retrieval and DB persistence are wired in on Day 3.
"""

import json
from collections.abc import AsyncGenerator

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings

# ── System prompt ─────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are DistroIQ, an AI operations assistant built for \
distribution companies. You help warehouse staff, operations managers, and \
logistics teams get instant, accurate answers from live operational data.

Your data sources include:
- Warehouse ERP: real-time stock levels, bin locations, reorder points, \
  stock movements, and SKU master data
- Order Management System (OMS): open orders, fulfilment status, shipment \
  tracking, backorders, and SLA breach risk
- Customer Database (CRM): account details, order history, credit limits, \
  and contact information
- Supplier Portal (EDI): purchase orders, supplier performance, lead times, \
  and inbound shipment ETAs
- Analytics Data Warehouse: historical trends, demand forecasts, and KPI \
  dashboards

Guidelines:
- Answer in clear, concise prose. Lead with the direct answer.
- When presenting multiple items, use a structured table if it aids clarity.
- Flag critical issues (stock-outs, SLA breaches, supplier delays) as alerts.
- If asked to draft a supplier or customer email, produce a professional \
  draft and label it clearly.
- Always cite which data source your answer is drawn from.
- If a question falls outside your operational data (e.g. HR, legal, finance \
  outside of credit limits), say so and redirect appropriately.
- Never fabricate inventory numbers, order statuses, or customer data. \
  If data is unavailable, say "I don't have that data right now" and suggest \
  who to contact.
- Keep responses focused on distribution operations: inventory, orders, \
  logistics, suppliers, and customers.

When returning structured data, format your response as JSON with this schema:
{
  "text": "<prose explanation>",
  "components": [
    // optional — include only when a richer UI element adds value
    { "type": "table", "headers": [...], "rows": [[...]], "statusCol": 2 },
    { "type": "alert", "alertType": "danger|warn|ok|info", "title": "...", \
"message": "..." },
    { "type": "email", "to": "...", "cc": "...", "subject": "...", "body": "..." },
    { "type": "citation", "sources": ["Warehouse ERP", "OMS"] }
  ]
}

If no structured components are needed, you may respond with plain prose."""

# ── LLM instance (module-level, reused across requests) ───────────────

_llm = ChatAnthropic(
    model=settings.ANTHROPIC_MODEL,
    api_key=settings.ANTHROPIC_API_KEY,
    streaming=True,
)


# ── Public coroutine ──────────────────────────────────────────────────

async def stream_chat(message: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Stream a Claude response for *message* token by token.

    Yields SSE-formatted strings.  Each yield is one complete SSE event
    (ending with the required double newline).
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ]

    try:
        async for chunk in _llm.astream(messages):
            # chunk.content is str for simple text, list for multi-part
            raw = chunk.content
            if isinstance(raw, str):
                text = raw
            elif isinstance(raw, list):
                text = "".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in raw
                )
            else:
                continue

            if text:
                yield f"data: {json.dumps({'type': 'delta', 'content': text})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as exc:  # noqa: BLE001
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
