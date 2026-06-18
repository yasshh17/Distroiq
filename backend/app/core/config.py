from functools import lru_cache
from typing import Any
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str
    REDIS_URL: str

    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    R2_BUCKET: str
    R2_ENDPOINT: str
    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str

    FRONTEND_URL: str = "http://localhost:3000"
    JWT_ALGORITHM: str = "HS256"

    @field_validator('SUPABASE_JWT_SECRET')
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
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
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://'"
            )
        return v.strip()

    @field_validator('ANTHROPIC_API_KEY')
    @classmethod
    def validate_anthropic_key(cls, v: str, info: ValidationInfo) -> str:
        if not v.startswith('sk-ant-api'):
            raise ValueError("ANTHROPIC_API_KEY must start with 'sk-ant-api'")
        return v.strip()

    @field_validator('SUPABASE_URL')
    @classmethod
    def validate_supabase_url(cls, v: str, info: ValidationInfo) -> str:
        if not v.startswith('https://') or not v.endswith('.supabase.co'):
            raise ValueError(
                "SUPABASE_URL must be https://*.supabase.co format"
            )
        return v.strip()

    def validate_critical_settings(self) -> None:
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
    config = Settings()
    config.validate_critical_settings()
    return config


settings: Settings = get_settings()
