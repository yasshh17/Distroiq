from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Liveness probe — returns immediately without hitting the DB."""
    return {"status": "ok", "version": settings.APP_VERSION}


@router.get("/health/db")
async def health_db():
    """Readiness probe — verifies the database connection is alive."""
    async for db in get_db():
        await db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
