"""
Pytest configuration for the DistroIQ backend test suite.

All required env vars are set here at *module level* — before any app
module is imported — so that pydantic-settings can parse Settings()
without raising a ValidationError for missing fields.

create_async_engine() (called when database.py is imported) only builds
the engine object; it does NOT open a connection, so a non-existent DB
URL is safe in unit tests that never actually execute queries.
"""

import os

_TEST_ENV: dict[str, str] = {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
    "REDIS_URL": "redis://localhost:6379/0",
    "ANTHROPIC_API_KEY": "sk-ant-test-00000000",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_JWT_SECRET": "test-jwt-secret-must-be-at-least-32-chars!!",
    "R2_BUCKET": "test-bucket",
    "R2_ENDPOINT": "https://test.r2.cloudflarestorage.com",
    "R2_ACCESS_KEY": "test-access-key-id",
    "R2_SECRET_KEY": "test-secret-access-key",
    "FRONTEND_URL": "http://localhost:3000",
}

for _key, _val in _TEST_ENV.items():
    os.environ.setdefault(_key, _val)
