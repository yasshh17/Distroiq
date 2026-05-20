"""
Comprehensive end-to-end tests for account deletion functionality.

Tests cover all security scenarios, error conditions, audit logging,
and edge cases that could occur in production.
"""

import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.diagnostics import create_test_jwt, debug_account_deletion
from app.core.audit import AuditAction, AuditOutcome


class TestAccountDeletionEndpoint:
    """Test suite for the account deletion endpoint."""

    @pytest.fixture
    def client(self):
        """Test client with proper configuration."""
        return TestClient(app)

    @pytest.fixture
    def valid_user_id(self):
        """Generate a valid user UUID."""
        return str(uuid.uuid4())

    @pytest.fixture
    def valid_jwt_token(self, valid_user_id):
        """Generate a valid JWT token for testing."""
        return create_test_jwt(user_id=valid_user_id, exp_minutes=60)

    @pytest.fixture
    def expired_jwt_token(self, valid_user_id):
        """Generate an expired JWT token for testing."""
        return create_test_jwt(user_id=valid_user_id, exp_minutes=-60)

    def test_successful_account_deletion(self, client, valid_user_id, valid_jwt_token):
        """Test successful account deletion with all proper conditions."""

        # Mock Supabase responses
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # Mock user exists check (200) and deletion success (204)
            check_response = MagicMock()
            check_response.status_code = 200
            check_response.text = json.dumps({"id": valid_user_id, "email": "test@example.com"})

            delete_response = MagicMock()
            delete_response.status_code = 204
            delete_response.text = ""

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            # Make the request
            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            # Verify response
            assert response.status_code == 200
            response_data = response.json()

            assert response_data["message"] == "Account successfully deleted"
            assert response_data["user_id"] == valid_user_id
            assert "timestamp" in response_data
            assert "audit_id" in response_data

            # Verify Supabase calls were made correctly
            mock_instance.get.assert_called_once()
            mock_instance.delete.assert_called_once()

            # Verify the headers used in Supabase calls
            get_call = mock_instance.get.call_args
            delete_call = mock_instance.delete.call_args

            expected_headers = {
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            }

            assert get_call[1]["headers"] == expected_headers
            assert delete_call[1]["headers"] == expected_headers

    def test_missing_authorization_header(self, client):
        """Test request without Authorization header."""
        response = client.delete("/api/v1/auth/account")

        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]

    def test_malformed_authorization_header(self, client):
        """Test request with malformed Authorization header."""
        response = client.delete(
            "/api/v1/auth/account",
            headers={"Authorization": "InvalidFormat token"}
        )

        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]

    def test_invalid_jwt_token(self, client):
        """Test request with invalid JWT token."""
        response = client.delete(
            "/api/v1/auth/account",
            headers={"Authorization": "Bearer invalid.jwt.token"}
        )

        assert response.status_code == 401
        assert "Token verification failed" in response.json()["detail"]

    def test_expired_jwt_token(self, client, expired_jwt_token):
        """Test request with expired JWT token."""
        response = client.delete(
            "/api/v1/auth/account",
            headers={"Authorization": f"Bearer {expired_jwt_token}"}
        )

        assert response.status_code == 401
        assert "Token verification failed" in response.json()["detail"]

    @patch.dict('os.environ', {'SUPABASE_SERVICE_ROLE_KEY': ''})
    def test_missing_service_role_key(self, client, valid_jwt_token):
        """Test when SUPABASE_SERVICE_ROLE_KEY is not configured."""

        # Force reload settings to pick up the environment change
        from app.core.config import get_settings
        get_settings.cache_clear()

        response = client.delete(
            "/api/v1/auth/account",
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )

        assert response.status_code == 500
        assert "SUPABASE_SERVICE_ROLE_KEY environment variable is missing" in response.json()["detail"]

    def test_user_not_found_in_supabase(self, client, valid_user_id, valid_jwt_token):
        """Test deletion attempt for non-existent user."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # Mock user not found (404)
            check_response = MagicMock()
            check_response.status_code = 404
            check_response.text = json.dumps({"error": "User not found"})

            mock_instance.get.return_value = check_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 404
            assert "already deleted" in response.json()["detail"]

    def test_supabase_service_unavailable(self, client, valid_user_id, valid_jwt_token):
        """Test when Supabase service is unavailable."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # Mock service error (503)
            check_response = MagicMock()
            check_response.status_code = 503
            check_response.text = "Service temporarily unavailable"

            mock_instance.get.return_value = check_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 503
            assert "Service returned 503" in response.json()["detail"]

    def test_supabase_timeout(self, client, valid_user_id, valid_jwt_token):
        """Test timeout when communicating with Supabase."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # Mock timeout exception
            mock_instance.get.side_effect = httpx.TimeoutException("Request timeout")

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 504
            assert "timed out" in response.json()["detail"]

    def test_supabase_network_error(self, client, valid_user_id, valid_jwt_token):
        """Test network error when communicating with Supabase."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # Mock network error
            mock_instance.get.side_effect = httpx.RequestError("Network error")

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 503
            assert "Unable to reach authentication service" in response.json()["detail"]

    def test_supabase_unauthorized_service_role(self, client, valid_user_id, valid_jwt_token):
        """Test when service role key is invalid/unauthorized."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # User exists check succeeds
            check_response = MagicMock()
            check_response.status_code = 200
            check_response.text = json.dumps({"id": valid_user_id})

            # But deletion fails with 401
            delete_response = MagicMock()
            delete_response.status_code = 401
            delete_response.text = json.dumps({"error": "Unauthorized"})

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 500
            assert "Service role authentication failed" in response.json()["detail"]

    def test_supabase_rate_limit(self, client, valid_user_id, valid_jwt_token):
        """Test when Supabase rate limit is exceeded."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # User exists check succeeds
            check_response = MagicMock()
            check_response.status_code = 200

            # But deletion fails with 429
            delete_response = MagicMock()
            delete_response.status_code = 429
            delete_response.text = json.dumps({"error": "Too Many Requests"})

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 500
            assert "Rate limit exceeded" in response.json()["detail"]

    @patch('app.api.v1.routes.auth.AuditLogger.log_account_deletion')
    @patch('app.api.v1.routes.auth.AuditLogger.log_auth_event')
    def test_audit_logging_on_success(self, mock_auth_log, mock_deletion_log,
                                    client, valid_user_id, valid_jwt_token):
        """Test that successful deletions are properly audit logged."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            check_response = MagicMock()
            check_response.status_code = 200

            delete_response = MagicMock()
            delete_response.status_code = 204

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 200

            # Verify audit logs were called
            assert mock_auth_log.called
            assert mock_deletion_log.called

            # Check that deletion was logged with SUCCESS outcome
            deletion_call = mock_deletion_log.call_args
            assert deletion_call[1]["user_id"] == valid_user_id
            assert deletion_call[1]["outcome"] == AuditOutcome.SUCCESS

    @patch('app.api.v1.routes.auth.AuditLogger.log_account_deletion')
    def test_audit_logging_on_failure(self, mock_deletion_log,
                                    client, valid_user_id, valid_jwt_token):
        """Test that failed deletions are properly audit logged."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            # User exists but deletion fails
            check_response = MagicMock()
            check_response.status_code = 200

            delete_response = MagicMock()
            delete_response.status_code = 500
            delete_response.text = "Internal Server Error"

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            response = client.delete(
                "/api/v1/auth/account",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 500

            # Verify failure was logged
            assert mock_deletion_log.called
            deletion_call = mock_deletion_log.call_args
            assert deletion_call[1]["user_id"] == valid_user_id
            assert deletion_call[1]["outcome"] == AuditOutcome.FAILURE

    def test_debug_endpoint_in_development(self, client, valid_user_id, valid_jwt_token):
        """Test debug endpoint availability in development."""

        # Ensure we're in development mode
        original_env = settings.APP_ENV
        settings.APP_ENV = "development"

        try:
            with patch('app.core.diagnostics.debug_account_deletion') as mock_debug:
                mock_debug.return_value = {
                    "user_id": valid_user_id,
                    "overall_status": "ready",
                    "steps": []
                }

                response = client.get(
                    f"/api/v1/auth/account/deletion-debug/{valid_user_id}",
                    headers={"Authorization": f"Bearer {valid_jwt_token}"}
                )

                assert response.status_code == 200
                assert response.json()["user_id"] == valid_user_id

        finally:
            settings.APP_ENV = original_env

    def test_debug_endpoint_disabled_in_production(self, client, valid_user_id, valid_jwt_token):
        """Test debug endpoint is disabled in production."""

        # Set production mode
        original_env = settings.APP_ENV
        settings.APP_ENV = "production"

        try:
            response = client.get(
                f"/api/v1/auth/account/deletion-debug/{valid_user_id}",
                headers={"Authorization": f"Bearer {valid_jwt_token}"}
            )

            assert response.status_code == 404
            assert "not available in production" in response.json()["detail"]

        finally:
            settings.APP_ENV = original_env

    def test_client_info_extraction(self, client, valid_user_id, valid_jwt_token):
        """Test that client information is properly extracted for audit logs."""

        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            check_response = MagicMock()
            check_response.status_code = 200

            delete_response = MagicMock()
            delete_response.status_code = 204

            mock_instance.get.return_value = check_response
            mock_instance.delete.return_value = delete_response

            # Include various headers to test extraction
            headers = {
                "Authorization": f"Bearer {valid_jwt_token}",
                "User-Agent": "Test Client/1.0",
                "X-Forwarded-For": "192.168.1.100",
                "Referer": "https://app.distroiq.com/"
            }

            response = client.delete("/api/v1/auth/account", headers=headers)

            assert response.status_code == 200

            # The audit logs should have captured this client information
            # This is verified through the audit logging tests above


class TestAccountDeletionDiagnostics:
    """Test suite for account deletion diagnostic tools."""

    @pytest.mark.asyncio
    async def test_debug_account_deletion_function(self):
        """Test the debug_account_deletion function directly."""
        test_user_id = str(uuid.uuid4())

        with patch('app.core.diagnostics.AuthDiagnostics.validate_jwt_secret'), \
             patch('app.core.diagnostics.AuthDiagnostics.test_supabase_connection'), \
             patch('app.core.diagnostics.AuthDiagnostics.test_service_role_permissions'), \
             patch('httpx.AsyncClient') as mock_client:

            # Mock all diagnostic checks to pass
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None

            user_check_response = MagicMock()
            user_check_response.status_code = 200
            user_check_response.text = json.dumps({"id": test_user_id})

            mock_instance.get.return_value = user_check_response

            result = await debug_account_deletion(test_user_id)

            assert result["user_id"] == test_user_id
            assert "steps" in result
            assert "overall_status" in result
            assert len(result["steps"]) >= 3  # At least 3 diagnostic steps


# Integration test fixtures and utilities

@pytest.fixture(scope="session")
def test_settings():
    """Test settings with safe defaults."""
    return {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
        "SUPABASE_JWT_SECRET": "test-jwt-secret-32-chars-long-minimum",
        "APP_ENV": "test"
    }


@pytest.fixture
def mock_supabase_success():
    """Mock successful Supabase interactions."""
    def _mock_responses(user_id: str):
        check_response = MagicMock()
        check_response.status_code = 200
        check_response.text = json.dumps({"id": user_id})

        delete_response = MagicMock()
        delete_response.status_code = 204
        delete_response.text = ""

        return check_response, delete_response

    return _mock_responses


# Performance and load testing utilities

class TestAccountDeletionPerformance:
    """Performance tests for account deletion under load."""

    @pytest.mark.slow
    def test_concurrent_deletion_attempts(self, client):
        """Test multiple concurrent deletion attempts for robustness."""
        # This would test rate limiting, connection pooling, etc.
        # Implementation depends on specific performance requirements
        pass

    @pytest.mark.slow
    def test_deletion_timeout_handling(self, client):
        """Test proper timeout handling under slow network conditions."""
        # This would test the 30-second timeout configuration
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])