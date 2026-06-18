import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.core.redis import init_redis, close_redis
from app.core.logging import setup_logging
from app.core.errors import (
    DistroIQException, distroiq_exception_handler,
    http_exception_handler, general_exception_handler
)
from app.api.v1.routes import health, chat, auth, files

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("DistroIQ API starting up")

    try:
        await init_redis()
        logger.info("Redis initialized successfully")
    except Exception as exc:
        logger.error(f"Failed to initialize Redis: {exc}")

    yield

    logger.info("DistroIQ API shutting down")
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="DistroIQ API",
    version=settings.APP_VERSION,
    description="AI-powered operations assistant for distribution companies.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "https://distroiq.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import HTTPException

app.add_exception_handler(DistroIQException, distroiq_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


_V1 = "/api/v1"

app.include_router(health.router, prefix=_V1)
app.include_router(chat.router, prefix=_V1)
app.include_router(auth.router, prefix=_V1)
app.include_router(files.router, prefix=_V1)
