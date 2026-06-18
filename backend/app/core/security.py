import json
import uuid
from typing import Any

import httpx
import jwt as pyjwt
from jwt.algorithms import ECAlgorithm

from app.core.config import settings


class AuthError(Exception):
    pass


_jwks_cache: dict | None = None


def verify_jwt(token: str) -> dict:
    global _jwks_cache

    try:
        header = pyjwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg", "ES256")

        if alg == "ES256":
            if not _jwks_cache:
                url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
                resp = httpx.get(url)
                resp.raise_for_status()
                _jwks_cache = resp.json()

            key_data = None
            for k in _jwks_cache.get("keys", []):
                if k.get("kid") == kid:
                    key_data = k
                    break

            if not key_data:
                raise AuthError("No matching key found in JWKS")

            public_key = ECAlgorithm.from_jwk(json.dumps(key_data))

            payload = pyjwt.decode(
                token,
                public_key,
                algorithms=["ES256"],
                options={"verify_aud": False},
            )
        else:
            # HS256 fallback for legacy tokens
            payload = pyjwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )

        return payload

    except AuthError:
        raise
    except Exception as exc:
        raise AuthError(str(exc)) from exc


def extract_user_id(payload: dict[str, Any]) -> uuid.UUID:
    try:
        return uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthError(f"Cannot extract user id from token: {exc}") from exc
