"""
Reusable FastAPI Depends callables.
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthError, extract_user_id, verify_jwt
from app.models.user import User

# ── Database ─────────────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]

# ── Auth ─────────────────────────────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: DBSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    """
    Validates the Bearer JWT and returns the corresponding User row.

    Raises 401 if the token is missing or invalid.
    Raises 404 if the user does not yet exist in the local DB
    (first-time Supabase login before the user record is created).
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_jwt(credentials.credentials)
        user_id: uuid.UUID = extract_user_id(payload)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found — complete registration first",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
