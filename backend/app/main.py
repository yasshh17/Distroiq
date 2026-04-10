from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.v1.routes import health, chat, auth, files


# ── Lifespan ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Verify the DB is reachable on startup; dispose the engine on shutdown."""
    async with engine.begin() as conn:
        await conn.execute(sa.text("SELECT 1"))

    yield

    await engine.dispose()


# ── App factory ───────────────────────────────────────────────────────

app = FastAPI(
    title="DistroIQ API",
    version=settings.APP_VERSION,
    description="AI-powered operations assistant for distribution companies.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────

_V1 = "/api/v1"

app.include_router(health.router, prefix=_V1)
app.include_router(chat.router, prefix=_V1)
app.include_router(auth.router, prefix=_V1)
app.include_router(files.router, prefix=_V1)
