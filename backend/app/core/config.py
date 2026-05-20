from functools import lru_cache
from typing import Any
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",  # Look in parent directory from backend/
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db

    # ── Redis ────────────────────────────────────────────────────────
    REDIS_URL: str  # redis://localhost:6379

    # ── Anthropic ────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # ── Supabase ─────────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ── Cloudflare R2 ────────────────────────────────────────────────
    R2_BUCKET: str
    R2_ENDPOINT: str  # https://<account>.r2.cloudflarestorage.com
    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str

    # ── Frontend ─────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Security ─────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"

    # ── Configuration Validators ─────────────────────────────────────

    @field_validator('SUPABASE_JWT_SECRET')
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        """Ensure JWT secret has no leading/trailing whitespace."""
        if not v:
            raise ValueError("SUPABASE_JWT_SECRET is required")

        original = v
        cleaned = v.strip()

        if original != cleaned:
            raise ValueError(
                f"SUPABASE_JWT_SECRET has leading/trailing whitespace. "
                f"Original length: {len(original)}, cleaned length: {len(cleaned)}. "
                f"Check your .env file for extra spaces."
            )

        if len(cleaned) < 32:
            raise ValueError("SUPABASE_JWT_SECRET appears too short (< 32 chars)")

        return cleaned

    @field_validator('SUPABASE_SERVICE_ROLE_KEY')
    @classmethod
    def validate_service_role_key(cls, v: str, info: ValidationInfo) -> str:
        """Ensure service role key is properly formatted for production."""
        if not v and os.getenv('APP_ENV') == 'production':
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is required in production for account deletion"
            )

        if v and (v.startswith(' ') or v.endswith(' ')):
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY has leading/trailing whitespace. "
                "Check your .env file for extra spaces."
            )

        return v.strip() if v else v

    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str, info: ValidationInfo) -> str:
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://'"
            )
        return v.strip()

    @field_validator('ANTHROPIC_API_KEY')
    @classmethod
    def validate_anthropic_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate Anthropic API key format."""
        if not v.startswith('sk-ant-api'):
            raise ValueError("ANTHROPIC_API_KEY must start with 'sk-ant-api'")
        return v.strip()

    @field_validator('SUPABASE_URL')
    @classmethod
    def validate_supabase_url(cls, v: str, info: ValidationInfo) -> str:
        """Validate Supabase URL format."""
        if not v.startswith('https://') or not v.endswith('.supabase.co'):
            raise ValueError(
                "SUPABASE_URL must be https://*.supabase.co format"
            )
        return v.strip()

    def validate_critical_settings(self) -> None:
        """Additional runtime validation for critical settings."""
        critical_for_auth = [
            'SUPABASE_URL',
            'SUPABASE_JWT_SECRET',
            'SUPABASE_ANON_KEY'
        ]

        missing = [key for key in critical_for_auth if not getattr(self, key)]
        if missing:
            raise ValueError(
                f"Missing critical authentication settings: {', '.join(missing)}"
            )


@lru_cache
def get_settings() -> Settings:
    """Get validated settings instance."""
    config = Settings()
    # Run additional validation checks
    config.validate_critical_settings()
    return config


# Global settings instance - will fail fast if configuration is invalid
settings: Settings = get_settings()
