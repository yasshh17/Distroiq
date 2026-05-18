from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings
from app.core.redis import get_redis
from app.workers.jobs import job_queue

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


@router.get("/health/redis")
async def health_redis():
    """Redis health check — verifies connection and basic operations."""
    try:
        redis = await get_redis()

        # Test basic operations
        test_key = "health:test"
        await redis.set(test_key, "ok", ex=60)
        value = await redis.get(test_key)
        await redis.delete(test_key)

        if value != "ok":
            raise HTTPException(status_code=500, detail="Redis read/write test failed")

        return {"status": "ok", "redis": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(exc)}")


@router.post("/health/queue-test")
async def test_queue():
    """Test ARQ job queue by enqueueing a test notification."""
    try:
        job_id = await job_queue.send_alert(
            alert_type="test",
            message="Health check test alert",
            user_id="health-check"
        )
        return {"status": "ok", "job_id": job_id, "message": "Test job enqueued"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Job queue test failed: {str(exc)}")


@router.get("/health/queue-status/{job_id}")
async def get_queue_status(job_id: str):
    """Get status of a queued job."""
    try:
        status = await job_queue.get_job_status(job_id)
        return {"status": "ok", "job": status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(exc)}")


@router.get("/health/debug")
async def debug_config():
    """Debug endpoint to show current configuration."""
    import os
    from pathlib import Path

    cwd = os.getcwd()
    env_file = Path(cwd).parent / ".env"
    env_exists = env_file.exists()

    redis_url = os.environ.get("REDIS_URL", "NOT_SET")
    config_redis = settings.REDIS_URL

    return {
        "cwd": cwd,
        "env_file_path": str(env_file),
        "env_file_exists": env_exists,
        "env_redis_url": redis_url[:50] + "..." if len(redis_url) > 50 else redis_url,
        "config_redis_url": config_redis[:50] + "..." if len(config_redis) > 50 else config_redis,
        "app_env": settings.APP_ENV,
    }
