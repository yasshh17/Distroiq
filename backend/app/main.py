import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.v1.routes import health, chat, auth, files

logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Start up the app; dispose the DB engine pool on shutdown."""
    logger.info("DistroIQ API starting up")

    yield

    logger.info("DistroIQ API shutting down")
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
