# DistroIQ

DistroIQ is an AI-powered operations assistant for distribution companies — employees ask plain-English questions and get structured answers sourced from live inventory, order, customer, and supplier data via a RAG pipeline. The system streams responses from Claude in real time, rendering rich UI components (tables, alerts, email drafts) directly in the chat.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14 (App Router), TypeScript strict, Tailwind CSS |
| **UI components** | shadcn/ui (new-york, zinc), DM Sans + DM Mono |
| **Client state** | Zustand |
| **Server state** | React Query |
| **Backend** | FastAPI (Python 3.12), async SQLAlchemy, Alembic |
| **AI / RAG** | LangChain, Anthropic Claude (`claude-sonnet-4-20250514`) |
| **Embeddings** | pgvector (PostgreSQL extension) |
| **Auth** | Supabase Auth + JWT |
| **Database** | PostgreSQL + Redis |
| **Storage** | Cloudflare R2 |
| **Job queue** | ARQ (async Redis queue) |
| **Hosting** | Vercel (frontend) · Render (backend) |
| **Secrets** | Doppler |

---

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 15+ with pgvector extension
- Redis 7+

### 1 — Clone and install

```bash
git clone <repo-url>
cd distroiq
```

### 2 — Frontend

```bash
# Install dependencies
npm install

# Copy env template and fill in values
cp .env.example .env.local

# Start the dev server (http://localhost:3000)
npm run dev
```

### 3 — Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env template and fill in values
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the API server (http://localhost:8000)
uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/api/docs` once the server is running.

---

## Environment Variables

Copy `.env.example` to `.env.local` (frontend) and `backend/.env.example` to `backend/.env` (backend), then fill in all values.

In production, frontend secrets are set in the Vercel dashboard and backend secrets in the Render dashboard. Do not commit `.env` files.

| Variable | Used by | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Frontend | Base URL of the FastAPI backend |
| `NEXT_PUBLIC_SUPABASE_URL` | Frontend | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend | Supabase public anon key |
| `ANTHROPIC_API_KEY` | Backend | Anthropic API key for Claude |
| `DATABASE_URL` | Backend | `postgresql+asyncpg://user:pass@host/db` |
| `REDIS_URL` | Backend | `redis://localhost:6379` |
| `SUPABASE_URL` | Backend | Supabase project URL |
| `SUPABASE_ANON_KEY` | Backend | Supabase public anon key |
| `SUPABASE_JWT_SECRET` | Backend | Used to verify Supabase JWTs server-side |
| `R2_BUCKET` | Backend | Cloudflare R2 bucket name |
| `R2_ENDPOINT` | Backend | `https://<account>.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY` | Backend | R2 access key ID |
| `R2_SECRET_KEY` | Backend | R2 secret access key |
| `FRONTEND_URL` | Backend | Allowed CORS origin (e.g. `https://distroiq.vercel.app`) |

---

## Deployment

### Frontend — Vercel

Vercel auto-deploys on every push to `main` via the GitHub integration. No manual steps are needed after the initial setup.

1. Import the repository at [vercel.com/new](https://vercel.com/new).
2. Vercel auto-detects Next.js from `vercel.json` — no build settings required.
3. Add environment variables in the Vercel dashboard (Project → Settings → Environment Variables):
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Backend — Render

The backend is defined in `backend/render.yaml`.

1. Create a new **Web Service** at [render.com](https://render.com) and connect the repository.
2. Set root directory to `backend` and let Render pick up `render.yaml`.
3. Add all backend environment variables in the Render dashboard.
4. Set the **pre-deploy command** to run migrations before each deploy:
   ```
   alembic upgrade head
   ```
5. Copy the **Deploy Hook URL** from the Render dashboard and add it as `RENDER_DEPLOY_HOOK_URL` in GitHub repository secrets — this is what the deploy workflow uses.

### Database — Supabase PostgreSQL

Supabase provides the PostgreSQL instance. After creating a project:
- Enable the `pgvector` extension: **Database → Extensions → vector**
- Use the **Session mode** connection string for `DATABASE_URL` (port `5432`)

### Redis — Upstash

Create a Redis database at [upstash.com](https://upstash.com) and copy the `rediss://` TLS URL into `REDIS_URL`.

### Health checks

| Service | URL |
|---|---|
| Frontend | `https://distroiq.vercel.app/` |
| Backend | `https://distroiq-backend.onrender.com/api/v1/health` |

---

## Project Structure

```
distroiq/
├── app/                        # Next.js App Router
│   ├── (auth)/login|signup
│   └── (dashboard)/layout.tsx + page.tsx
├── components/
│   ├── ui/                     # shadcn/ui primitives
│   └── features/chat/          # Chat UI components
├── lib/api.ts                  # Axios instance
├── stores/                     # Zustand stores
├── types/index.ts
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/      # FastAPI route handlers
│   │   ├── core/               # Config, DB, security, deps
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   └── services/           # AI/RAG pipeline, R2 storage
│   ├── alembic/                # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── vercel.json                 # Vercel deployment config (frontend)
├── backend/render.yaml         # Render deployment config (backend)
└── CLAUDE.md                   # AI assistant context
```
