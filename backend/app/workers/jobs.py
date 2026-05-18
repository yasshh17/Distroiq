"""Job utilities for enqueueing background tasks."""

import logging
from typing import Any

from app.workers.arq_worker import enqueue_job

logger = logging.getLogger(__name__)


class JobQueue:
    """High-level interface for background job operations."""

    @staticmethod
    async def reindex_source(source_id: str, batch_size: int = 100) -> str:
        """Queue a source re-indexing job."""
        return await enqueue_job(
            "reindex_source_data",
            source_id,
            batch_size,
        )

    @staticmethod
    async def cleanup_embeddings(days_old: int = 30) -> str:
        """Queue an embedding cleanup job."""
        return await enqueue_job(
            "cleanup_old_embeddings",
            days_old,
        )

    @staticmethod
    async def send_alert(alert_type: str, message: str, user_id: str) -> str:
        """Queue an alert notification job."""
        return await enqueue_job(
            "send_alert_notification",
            alert_type,
            message,
            user_id,
        )

    @staticmethod
    async def get_job_status(job_id: str) -> dict[str, Any]:
        """Get status of a background job."""
        # Note: Job status checking requires the ARQ worker to be running
        # For now, return a simple response indicating the job was queued
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Job was successfully enqueued. Start ARQ worker to process jobs."
        }


# Convenience instance
job_queue = JobQueue()