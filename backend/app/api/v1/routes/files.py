"""
File upload endpoints — placeholder.

Will be implemented when Cloudflare R2 storage is wired up.

Planned endpoints:
  POST /files/upload          → get a presigned R2 URL for direct upload
  GET  /files/{key}           → get a presigned R2 URL for download
  DELETE /files/{key}         → delete an object from R2
"""

from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])
