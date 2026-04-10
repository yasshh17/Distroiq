"""
Auth endpoints — placeholder.

Supabase handles the actual auth flow (sign-up, sign-in, OAuth).
These endpoints handle post-auth tasks:
  POST /auth/register  → upsert User row after Supabase sign-up
  GET  /auth/me        → return the current user's profile
  PUT  /auth/me        → update profile fields (full_name, etc.)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
