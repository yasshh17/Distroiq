"""
Tests for the /api/v1/health endpoint.

Uses a minimal FastAPI app that mounts only the health router — no
lifespan handler, no database connection. This keeps the test fully
self-contained and runnable in CI without a live PostgreSQL instance.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.routes.health import router

# Minimal app: no lifespan, no middleware, just the health router.
_app = FastAPI()
_app.include_router(router, prefix="/api/v1")

client = TestClient(_app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
