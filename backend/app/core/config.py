from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    # ── Cloudflare R2 ────────────────────────────────────────────────
    R2_BUCKET: str
    R2_ENDPOINT: str  # https://<account>.r2.cloudflarestorage.com
    R2_ACCESS_KEY: str
    R2_SECRET_KEY: str

    # ── Frontend ─────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Security ─────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
