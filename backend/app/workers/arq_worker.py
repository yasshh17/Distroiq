"""ARQ worker configuration and job definitions for DistroIQ."""

import logging
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import Worker
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    """Create RedisSettings from REDIS_URL for ARQ."""
    parsed = urlparse(settings.REDIS_URL)

    # Extract password from URL (format: redis://user:pass@host:port)
    password = parsed.password

    # Determine SSL based on scheme
    use_ssl = parsed.scheme in ("rediss", "redis+tls", "https")

    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or (6380 if use_ssl else 6379),
        password=password,
        ssl=use_ssl,
    )


# ── Job definitions ───────────────────────────────────────────────────


async def reindex_source_data(ctx: dict[str, Any], source_id: str, batch_size: int = 100) -> str:
    """Re-index all documents from a connected data source."""
    logger.info(f"Starting re-indexing for source: {source_id}")

    try:
        # TODO: Implement actual re-indexing logic
        # 1. Connect to data source (ERP, OMS, CRM, etc.)
        # 2. Fetch documents in batches
        # 3. Generate embeddings via LangChain
        # 4. Store in pgvector

        # Placeholder implementation
        import asyncio
        await asyncio.sleep(2)  # Simulate processing time

        logger.info(f"Completed re-indexing for source: {source_id}")
        return f"Successfully re-indexed source {source_id}"

    except Exception as exc:
        logger.error(f"Failed to re-index source {source_id}: {exc}")
        raise


async def cleanup_old_embeddings(ctx: dict[str, Any], days_old: int = 30) -> str:
    """Clean up embedding vectors older than specified days."""
    logger.info(f"Starting cleanup of embeddings older than {days_old} days")

    try:
        # TODO: Implement cleanup logic
        # 1. Connect to PostgreSQL
        # 2. Delete old embedding records
        # 3. Update source metadata

        # Placeholder implementation
        import asyncio
        await asyncio.sleep(1)

        logger.info(f"Completed cleanup of old embeddings")
        return f"Cleaned up embeddings older than {days_old} days"

    except Exception as exc:
        logger.error(f"Failed to cleanup embeddings: {exc}")
        raise


async def send_alert_notification(ctx: dict[str, Any], alert_type: str, message: str, user_id: str) -> str:
    """Send alert notification to user."""
    logger.info(f"Sending {alert_type} alert to user {user_id}")

    try:
        # TODO: Implement notification logic
        # 1. Determine notification channels (email, Slack, etc.)
        # 2. Send via appropriate service
        # 3. Log delivery status

        # Placeholder implementation
        import asyncio
        await asyncio.sleep(0.5)

        logger.info(f"Sent {alert_type} alert to user {user_id}")
        return f"Alert sent to {user_id}"

    except Exception as exc:
        logger.error(f"Failed to send alert: {exc}")
        raise


# ── ARQ settings ──────────────────────────────────────────────────────

class WorkerSettings:
    """ARQ worker configuration."""

    # Job functions
    functions = [
        reindex_source_data,
        cleanup_old_embeddings,
        send_alert_notification,
    ]

    # Redis connection
    redis_settings = get_redis_settings()

    # Worker settings
    max_jobs = 10
    job_timeout = 600  # 10 minutes
    keep_result = 3600  # Keep results for 1 hour
    queue_name = "distroiq:jobs"

    # Logging
    log_results = True
    verbose = True


async def enqueue_job(function_name: str, *args, **kwargs) -> str:
    """Enqueue a job for background processing."""
    redis = await create_pool(WorkerSettings.redis_settings)

    try:
        job = await redis.enqueue_job(function_name, *args, **kwargs)
        logger.info(f"Enqueued job {function_name} with ID: {job.job_id}")
        return job.job_id
    finally:
        await redis.close()


# ── CLI entry point ────────────────────────────────────────────────────

async def run_worker():
    """Run the ARQ worker. Used by: python -m arq app.workers.arq_worker.WorkerSettings"""
    worker = Worker(
        functions=WorkerSettings.functions,
        redis_settings=WorkerSettings.redis_settings,
        max_jobs=WorkerSettings.max_jobs,
        job_timeout=WorkerSettings.job_timeout,
        keep_result=WorkerSettings.keep_result,
        queue_name=WorkerSettings.queue_name,
    )

    logger.info("Starting ARQ worker...")
    await worker.async_run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_worker())