"""
Auth endpoints.

Supabase handles the actual auth flow (sign-up, sign-in, OAuth).
These endpoints handle post-auth tasks:
  DELETE /auth/account  → delete the authenticated user from Supabase auth.users
"""

from typing import Annotated

import httpx
from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.core.security import AuthError, extract_user_id, verify_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    """
    Permanently delete the authenticated user from Supabase auth.users.

    Uses JWT-only auth (no DB lookup) so it works without a local
    PostgreSQL instance. The service role key is used server-side only —
    it is never exposed to the frontend.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    token = authorization[len("bearer "):].strip()
    try:
        payload = verify_jwt(token)
        user_id = str(extract_user_id(payload))
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion not configured",
        )

    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers={
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            },
        )

    if resp.status_code not in (200, 204):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        )
