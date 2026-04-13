# DistroIQ

**AI-powered operations assistant for distribution companies.**  
Ask plain-English questions. Get instant answers from live inventory, orders, customers, and supplier data.

🔗 **Live Demo:** https://distroiq.vercel.app  
📁 **Backend API:** https://distroiq.onrender.com/api/v1/health

---

## What It Does

Distribution operations teams spend hours hunting through ERP dashboards, spreadsheets, and supplier portals to answer simple questions like:
- "Which SKUs are critically low right now?"
- "Which customers haven't reordered in 60 days?"
- "Draft a reorder email to our supplier for SKU MO-7"

DistroIQ replaces that with a single chat interface. Type a question, get a structured answer with tables, alerts, and actionable data — streamed in real time.

---

## Architecture
┌─────────────────────────────────────────────────────────────┐
│                        Browser Client                        │
│                    Next.js 14 + TypeScript                   │
│         Zustand state · shadcn/ui · Tailwind CSS             │
└─────────────────────┬───────────────────────────────────────┘
│  SSE streaming (fetch + ReadableStream)
│  JWT Bearer token (Supabase Auth)
┌─────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                         │
│                    Python 3.12 · Uvicorn                     │
│         JWT verification · CORS · SSE endpoint              │
└─────────────────────┬───────────────────────────────────────┘
│  LangChain astream()
┌─────────────────────▼───────────────────────────────────────┐
│                    LangChain + Claude                        │
│           claude-sonnet-4-20250514 · Streaming              │
│      System prompt · JSON schema enforcement                 │
└─────────────────────────────────────────────────────────────┘
Auth:     Supabase Auth (ES256 JWT · PKCE flow)
Hosting:  Vercel (frontend) · Render (backend)
CI/CD:    GitHub Actions (lint → build → deploy)

## Response Pipeline

Every query follows this flow:
User types query
↓
Frontend adds user message + empty AI message (isStreaming: true)
↓
GET /api/v1/chat/stream?message=... (with Bearer JWT)
↓
FastAPI verifies JWT via Supabase JWKS endpoint (ES256)
↓
LangChain builds [SystemMessage, HumanMessage]
↓
Claude streams tokens via astream()
↓
SSE delta events → frontend accumulates content
↓
SSE done event → JSON parsed → rich components rendered
↓
User sees: prose + data table + alert banner + source citation

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript strict |
| Styling | Tailwind CSS, shadcn/ui (new-york/zinc) |
| State | Zustand, React hooks |
| Backend | FastAPI, Python 3.12, Uvicorn |
| AI | LangChain, Anthropic Claude (claude-sonnet-4-20250514) |
| Auth | Supabase Auth, ES256 JWT, PKCE |
| Streaming | Server-Sent Events, fetch ReadableStream |
| Hosting | Vercel + Render |
| CI/CD | GitHub Actions |

## Key Features

- **Streaming AI responses** — tokens stream word by word, 
  rendered only after completion to avoid raw JSON flash
- **Rich component rendering** — AI responses parse into 
  tables, alert banners, email drafts, and source citations
- **JWT auth** — ES256 asymmetric verification via Supabase 
  JWKS endpoint, no secrets needed on the verify side
- **Full auth flow** — signup, login, forgot password, 
  reset password, delete account
- **Mobile responsive** — hamburger nav, scrollable tabs, 
  single-column layout on mobile
- **Keep-alive** — health ping every 10 minutes prevents 
  Render free tier spin-down during demos

## Project Structure
├── app/
│   ├── (auth)/          # login, signup, forgot-password, reset-password
│   └── (dashboard)/     # main chat interface
├── components/
│   ├── features/
│   │   ├── auth/        # UserChip, DeleteAccountModal, AuthProvider
│   │   ├── chat/        # AIBubble, UserBubble, DataTable, AlertBanner
│   │   └── sidebar/     # QuickQueriesPanel, source indicators
│   └── ui/              # shadcn/ui primitives
├── stores/
│   ├── auth.ts          # Zustand auth state
│   └── chat.ts          # Zustand chat + streaming state
├── lib/
│   ├── api.ts           # Axios instance
│   └── supabase/        # client, server, middleware
└── backend/
    ├── app/
    │   ├── api/v1/routes/   # chat.py, auth.py, health.py
    │   ├── core/            # config, security (JWKS verify), dependencies
    │   └── services/ai/     # chain.py (LangChain + Claude)

## Local Development

### Prerequisites
- Node.js 20+
- Python 3.12
- Supabase project

### Frontend

```bash
npm install
cp .env.example .env.local
# Fill in NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY,
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_JWT_SECRET,
# SUPABASE_SERVICE_ROLE_KEY
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Environment Variables

| Variable | Where | Description |
|---|---|---|
| NEXT_PUBLIC_SUPABASE_URL | frontend | Supabase project URL |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | frontend | Supabase anon key |
| NEXT_PUBLIC_API_URL | frontend | Backend URL |
| ANTHROPIC_API_KEY | backend | Claude API key |
| SUPABASE_URL | backend | Supabase project URL |
| SUPABASE_JWT_SECRET | backend | Legacy HS256 secret (fallback) |
| SUPABASE_SERVICE_ROLE_KEY | backend | For account deletion |

## Deployment

**Frontend → Vercel**  
Connects to GitHub, auto-deploys on push to main.  
Set all `NEXT_PUBLIC_*` env vars in Vercel dashboard.

**Backend → Render**  
Free tier web service, auto-deploys from GitHub.  
Set all backend env vars in Render dashboard.  
Set `FRONTEND_URL=https://distroiq.vercel.app` for CORS.

---
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Built With

- [Claude Code](https://claude.ai/code) — AI-powered development assistant
- [Anthropic Claude](https://anthropic.com) — Large language model for AI responses
- [Next.js](https://nextjs.org) — React framework
- [FastAPI](https://fastapi.tiangolo.com) — Python web framework
- [Supabase](https://supabase.com) — Backend-as-a-Service
- [Vercel](https://vercel.com) + [Render](https://render.com) — Hosting platforms

---

**Made with ❤️ for distribution teams everywhere**
