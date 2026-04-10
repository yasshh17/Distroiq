"""
Cloudflare R2 storage — placeholder.

Will use boto3 with the R2-compatible S3 API.
All credentials are read from Settings (R2_BUCKET, R2_ENDPOINT,
R2_ACCESS_KEY, R2_SECRET_KEY).
"""

from __future__ import annotations


async def generate_presigned_upload_url(
    key: str,
    content_type: str,
    expires_in: int = 3600,
) -> str:
    """Return a presigned PUT URL for direct browser-to-R2 upload."""
    raise NotImplementedError("R2 storage not yet implemented")


async def generate_presigned_download_url(
    key: str,
    expires_in: int = 3600,
) -> str:
    """Return a presigned GET URL for time-limited file access."""
    raise NotImplementedError("R2 storage not yet implemented")


async def delete_object(key: str) -> None:
    """Permanently delete an object from the R2 bucket."""
    raise NotImplementedError("R2 storage not yet implemented")
