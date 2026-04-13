# CLAUDE.md — DistroIQ

## 0. Claude Code Instructions
- Always read this entire file before starting any task
- Check .claude/rules/ for the relevant rule file before writing code
- Never run database migrations without explicit user confirmation
- Never commit secrets or .env files
- Run `npm run build` after any frontend changes to catch type errors
- Run `.venv/bin/python -c "from app.main import app; print('OK')"` after any backend changes

---

## 1. Project Overview

DistroIQ is an AI-powered operations assistant for distribution companies. Employees ask plain-English questions and receive structured answers sourced from live inventory, order, customer, and supplier data via a RAG (Retrieval-Augmented Generation) pipeline. The system connects to real ERP, OMS, CRM, and EDI data sources and streams responses back to the browser as they are generated.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Next.js 14 (App Router) |
| **Language** | TypeScript — `strict: true` throughout |
| **Styling** | Tailwind CSS + shadcn/ui (new-york style, zinc base) |
| **Fonts** | DM Sans (300/400/500/600) · DM Mono (400/500) |
| **Client state** | Zustand |
| **Data fetching** | React Query (to be added) |
| **Backend** | FastAPI (Python), async SQLAlchemy, Alembic, asyncpg |
| **AI / RAG** | LangChain, Anthropic Claude (`claude-sonnet-4-20250514`) |
| **Embeddings** | pgvector (PostgreSQL extension) |
| **Auth** | Supabase Auth with JWT |
| **Database** | PostgreSQL + Redis |
| **Storage** | Cloudflare R2 |
| **Job queue** | ARQ (async Redis queue) |
| **Hosting** | Vercel (frontend) · Render (backend) |
| **CI/CD** | GitHub Actions |
| **Env secrets** | Doppler |

---

## 3. Folder Structure

### Frontend (current)

```
app/
  (auth)/
    login/page.tsx
    signup/page.tsx
  (dashboard)/
    layout.tsx          # Shell: header + dark navy sidebar + main slot
    page.tsx            # Chat area: toolbar, message list, input bar
  layout.tsx            # Root: DM Sans/Mono fonts, globals.css
  globals.css           # Tailwind base + shadcn/ui CSS variables (zinc)
components/
  ui/                   # shadcn/ui primitives (Button, Dialog, etc.)
  features/
    chat/
      WelcomeScreen.tsx
      MessageRow.tsx
      UserBubble.tsx
      AIBubble.tsx
      DataTable.tsx
      AlertBanner.tsx
      EmailCard.tsx
      SourceCitation.tsx
      StatusBadge.tsx
      TypingIndicator.tsx
    sidebar/            # Sidebar subcomponents (sources, alerts, queries)
lib/
  api.ts                # Axios instance — all API calls go through here
  utils.ts              # cn() and shared utilities
stores/
  chat.ts               # Zustand: message history, streaming state
  auth.ts               # Zustand: current user, JWT token
types/
  index.ts              # Shared TypeScript interfaces and enums
```

### Backend (planned — Prompt 4)

```
backend/
  app/
    main.py             # FastAPI app factory, lifespan, CORS
    api/
      v1/
        chat.py         # POST /chat, GET /chat/stream (SSE)
        auth.py         # JWT validation middleware
        sources.py      # Connected source health + record counts
    core/
      config.py         # Pydantic Settings (reads from Doppler/env)
      database.py       # Async SQLAlchemy engine + session factory
      redis.py          # Redis connection pool
    models/
      message.py        # SQLAlchemy: Message, Session
      source.py         # ConnectedSource
    schemas/
      chat.py           # Pydantic v2: ChatRequest, ChatResponse, StreamChunk
    rag/
      pipeline.py       # LangChain retrieval chain (pgvector + Claude)
      embedder.py       # Text → pgvector embedding
      retriever.py      # pgvector similarity search
      prompt.py         # System prompt templates
    workers/
      arq_worker.py     # ARQ job definitions (re-indexing, bulk ops)
  alembic/              # Database migrations
  tests/
```

---

## 4. Coding Conventions

These are hard rules — do not deviate without a documented reason.

### TypeScript / React

- **Named exports everywhere** except `page.tsx` and `layout.tsx` files, which use default exports (Next.js requirement).
- **`"use client"` only when strictly necessary** — event handlers, browser APIs, or React hooks that cannot run on the server. Prefer server components by default.
- **Never use `any`** — type everything explicitly. Use `unknown` + narrowing when the type is genuinely unknown.
- **Interfaces over type aliases** for object shapes. Use `type` only for unions, intersections, or utility types.
- **Co-locate component interfaces** with their file unless the type is shared across multiple files — in that case, put it in `types/index.ts`.
- **No inline styles** — Tailwind utility classes only. Exception: `style` prop is allowed only for dynamic values that cannot be expressed as Tailwind classes (e.g., `box-shadow` with runtime values, `animation-delay` values from JS).

### Styling

- **Tailwind only** — no CSS modules, no styled-components, no `<style>` tags.
- **DM Mono (`font-mono`)** for all: badges, labels, timestamps, monospace values, code, status indicators, counts.
- **DM Sans (`font-sans`)** for all body text, headings, and UI copy.
- **Sidebar and header background**: `#0f1623` (dark navy) — use the literal hex or a Tailwind arbitrary value `bg-[#0f1623]`.
- **Primary accent**: `#2563eb` (blue-600) — use Tailwind `blue-600` scale.
- **shadcn/ui components** go in `components/ui/`. Do not add custom logic to shadcn primitives — wrap them instead.

### State & Data

- **All API calls** go through the Axios instance in `lib/api.ts`. Never call `fetch` directly in components.
- **One Zustand store per domain** in `stores/`. Keep stores flat — no nested state objects deeper than one level.
- **React Query** handles server state (caching, loading, error). Zustand handles client/UI state only (e.g., active tab, sidebar open state, current session ID).

### Backend (Python)

- **`snake_case`** for all variables, functions, and filenames.
- **Pydantic v2** for all schemas — use `model_validator`, `field_validator`, and `model_config` (not v1 `@validator` / `class Config`).
- **Async SQLAlchemy sessions** everywhere — no synchronous ORM calls.
- **Never commit secrets** — all secrets are managed by Doppler and injected as environment variables. The `.env.local` file is for local development only and is gitignored.

---

## 5. What's Built

| Area | Status | Notes |
|---|---|---|
| Next.js 14 scaffold | ✅ Done | TypeScript strict, Tailwind, ESLint + Prettier, shadcn/ui config |
| Google Fonts | ✅ Done | DM Sans + DM Mono via `next/font/google` in root layout |
| Dashboard shell | ✅ Done | Dark navy sidebar (260px), full-width header, chat main area |
| Sidebar content | ✅ Done | Connected Sources, Live Alerts, Quick Queries (placeholder data) |
| Chat toolbar | ✅ Done | Filter tabs (All / Inventory / Orders / Customers / Suppliers / Actions) |
| Welcome screen | ✅ Done | DQ glow icon, heading, subtitle, 2×2 query cards, footer |
| Chat components | ✅ Done | MessageRow, UserBubble, AIBubble, DataTable, AlertBanner, EmailCard, SourceCitation, StatusBadge, TypingIndicator |
| Zustand stores | ✅ Scaffolded | `chat.ts` and `auth.ts` — empty, ready for state |
| Axios instance | ✅ Done | `lib/api.ts` — base URL from `NEXT_PUBLIC_API_URL` env |
| Auth pages | ✅ Scaffolded | `/login` and `/signup` — empty pages, routes registered |

---

## 6. What's Next (In Order)

1. **Chat interaction** — wire `chat.ts` Zustand store, render `MessageRow` list from state, connect input textarea to store actions.
2. **FastAPI backend scaffold** — `main.py`, async DB session, Pydantic settings from Doppler, health endpoint.
3. **SQLAlchemy models + Alembic** — `Message`, `ChatSession`, `ConnectedSource` tables, initial migration.
4. **Supabase Auth end-to-end** — `signup/login` pages with Supabase client, JWT stored in Zustand `auth.ts`, Axios request interceptor attaches `Authorization: Bearer`.
5. **LangChain RAG pipeline** — pgvector retriever, prompt template, Claude streaming via `claude-sonnet-4-20250514`, SSE endpoint `GET /chat/stream`.
6. **Frontend streaming** — `EventSource` in `chat.ts` store, token-by-token append to `AIBubble`, show `TypingBubble` while awaiting first token.
7. **pgvector embeddings** — embed source documents on ingest, store in `pg_embedding` table, similarity search in retriever.
8. **Cloudflare R2 uploads** — presigned URL endpoint, file attachment UI in input bar.
9. **ARQ job queue** — background re-indexing jobs triggered on source data change.
10. **CI/CD** — GitHub Actions: lint → type-check → test → Render deploy hook on merge to `main`. Frontend deploys automatically via Vercel GitHub integration.

---

## 7. Key Design Decisions

### RAG Architecture

Each query goes through a four-step pipeline:

1. **Embed** — the user's query is converted to a vector via an embedding model.
2. **Retrieve** — pgvector similarity search returns the top-k relevant document chunks from the connected data sources (ERP, OMS, CRM, EDI).
3. **Augment** — retrieved chunks are injected into a structured system prompt alongside the query.
4. **Generate** — Claude (`claude-sonnet-4-20250514`) produces a response that is constrained to only cite retrieved data.

The retriever is source-aware: it tags each chunk with its origin (`warehouse_erp`, `order_management`, `customer_db`, etc.) so the frontend can render accurate `SourceCitation` tags.

### JSON Response Schema

Claude is instructed to return structured JSON rather than free prose. The schema allows the frontend to render rich components directly:

```jsonc
{
  "text": "string",          // prose explanation (always present)
  "components": [            // optional — rendered in order below the text
    { "type": "table",       "headers": [], "rows": [], "statusCol": 2 },
    { "type": "alert",       "alertType": "danger|warn|ok|info", "title": "", "message": "" },
    { "type": "email",       "to": "", "cc": "", "subject": "", "body": "" },
    { "type": "citation",    "sources": [] }
  ]
}
```

The frontend `AIBubble` renders `text` as prose, then maps `components` to `DataTable`, `AlertBanner`, `EmailCard`, and `SourceCitation` respectively.

### Streaming Approach

Responses are streamed via **Server-Sent Events (SSE)** from `GET /api/v1/chat/stream`. The backend uses LangChain's `astream` to yield tokens as they arrive from Claude. Each SSE event is one of:

- `delta` — a token chunk to append to the current AI message
- `component` — a fully-formed JSON component object (sent after prose, before stream close)
- `done` — signals stream completion; frontend marks the message as complete and hides `TypingBubble`
- `error` — stream-level error; frontend renders an `AlertBanner` with `type="danger"`

The frontend holds an `EventSource` connection in the `chat.ts` Zustand store for the duration of the response. On `done` or `error`, the connection is closed and the session timer updates.
