"""
JWT verification using Supabase's JWT secret.

Supabase issues JWTs signed with HS256 and the SUPABASE_JWT_SECRET.
The `sub` claim contains the Supabase user UUID.
"""

import uuid
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


class AuthError(Exception):
    """Raised when a token cannot be verified."""


def verify_jwt(token: str) -> dict[str, Any]:
    """
    Decode and verify a Supabase-issued JWT.

    Returns the decoded payload on success.
    Raises AuthError on any verification failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},  # Supabase sets aud: "authenticated"
        )
    except JWTError as exc:
        raise AuthError(f"Invalid token: {exc}") from exc

    if payload.get("sub") is None:
        raise AuthError("Token missing 'sub' claim")

    return payload


def extract_user_id(payload: dict[str, Any]) -> uuid.UUID:
    """Return the Supabase user UUID from a decoded JWT payload."""
    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthError(f"Cannot extract user id from token: {exc}") from exc
