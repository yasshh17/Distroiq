"""
Diagnostic utilities for troubleshooting and monitoring.

Provides tools for validating system health, testing integrations,
and debugging issues in development and production.
"""

import asyncio
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

import httpx
import jwt as pyjwt

from app.core.config import settings
from app.core.logging import log_auth_event, log_security_event


class DiagnosticResult:
    """Container for diagnostic test results."""

    def __init__(self, name: str, passed: bool, details: Dict[str, Any]):
        self.name = name
        self.passed = passed
        self.details = details
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} {self.name}: {self.details.get('message', 'No details')}"


class AuthDiagnostics:
    """Diagnostic tools for authentication system."""

    @staticmethod
    def validate_jwt_secret() -> DiagnosticResult:
        """Validate JWT secret configuration."""
        try:
            secret = settings.SUPABASE_JWT_SECRET

            if not secret:
                return DiagnosticResult(
                    "JWT Secret Validation",
                    False,
                    {"message": "JWT secret is empty", "error": "MISSING_SECRET"}
                )

            if secret.startswith(' ') or secret.endswith(' '):
                return DiagnosticResult(
                    "JWT Secret Validation",
                    False,
                    {
                        "message": "JWT secret has whitespace padding",
                        "error": "WHITESPACE_PADDING",
                        "length": len(secret),
                        "trimmed_length": len(secret.strip())
                    }
                )

            if len(secret) < 32:
                return DiagnosticResult(
                    "JWT Secret Validation",
                    False,
                    {
                        "message": "JWT secret appears too short",
                        "error": "SECRET_TOO_SHORT",
                        "length": len(secret)
                    }
                )

            # Test JWT creation/verification
            test_payload = {"sub": str(uuid.uuid4()), "exp": int(time.time()) + 300}
            test_token = pyjwt.encode(test_payload, secret, algorithm="HS256")
            decoded = pyjwt.decode(test_token, secret, algorithms=["HS256"])

            if decoded["sub"] != test_payload["sub"]:
                return DiagnosticResult(
                    "JWT Secret Validation",
                    False,
                    {
                        "message": "JWT encode/decode mismatch",
                        "error": "ENCODE_DECODE_MISMATCH"
                    }
                )

            return DiagnosticResult(
                "JWT Secret Validation",
                True,
                {
                    "message": "JWT secret is valid and working",
                    "length": len(secret),
                    "algorithm": "HS256"
                }
            )

        except Exception as e:
            return DiagnosticResult(
                "JWT Secret Validation",
                False,
                {"message": f"JWT validation error: {str(e)}", "error": "VALIDATION_EXCEPTION"}
            )

    @staticmethod
    async def test_supabase_connection() -> DiagnosticResult:
        """Test connection to Supabase."""
        try:
            async with httpx.AsyncClient() as client:
                # Test basic connectivity
                response = await client.get(
                    f"{settings.SUPABASE_URL}/auth/v1/settings",
                    headers={"apikey": settings.SUPABASE_ANON_KEY},
                    timeout=10
                )

                if response.status_code != 200:
                    return DiagnosticResult(
                        "Supabase Connection",
                        False,
                        {
                            "message": f"Supabase API returned {response.status_code}",
                            "status_code": response.status_code,
                            "response": response.text[:200]
                        }
                    )

                return DiagnosticResult(
                    "Supabase Connection",
                    True,
                    {
                        "message": "Successfully connected to Supabase",
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                )

        except httpx.TimeoutException:
            return DiagnosticResult(
                "Supabase Connection",
                False,
                {"message": "Connection to Supabase timed out", "error": "TIMEOUT"}
            )
        except Exception as e:
            return DiagnosticResult(
                "Supabase Connection",
                False,
                {"message": f"Supabase connection error: {str(e)}", "error": "CONNECTION_EXCEPTION"}
            )

    @staticmethod
    async def test_service_role_permissions() -> DiagnosticResult:
        """Test if service role key has proper permissions."""
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            return DiagnosticResult(
                "Service Role Permissions",
                False,
                {"message": "Service role key not configured", "error": "MISSING_KEY"}
            )

        try:
            # Test admin endpoints access
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.SUPABASE_URL}/auth/v1/admin/users",
                    headers={
                        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                    },
                    params={"page": 1, "per_page": 1},  # Minimal query
                    timeout=10
                )

                if response.status_code == 401:
                    return DiagnosticResult(
                        "Service Role Permissions",
                        False,
                        {
                            "message": "Service role key authentication failed",
                            "error": "UNAUTHORIZED",
                            "status_code": response.status_code
                        }
                    )

                if response.status_code == 403:
                    return DiagnosticResult(
                        "Service Role Permissions",
                        False,
                        {
                            "message": "Service role key lacks admin permissions",
                            "error": "INSUFFICIENT_PERMISSIONS",
                            "status_code": response.status_code
                        }
                    )

                if response.status_code != 200:
                    return DiagnosticResult(
                        "Service Role Permissions",
                        False,
                        {
                            "message": f"Unexpected response: {response.status_code}",
                            "error": "UNEXPECTED_RESPONSE",
                            "status_code": response.status_code,
                            "response": response.text[:200]
                        }
                    )

                return DiagnosticResult(
                    "Service Role Permissions",
                    True,
                    {
                        "message": "Service role has proper admin permissions",
                        "status_code": response.status_code
                    }
                )

        except Exception as e:
            return DiagnosticResult(
                "Service Role Permissions",
                False,
                {"message": f"Permission test error: {str(e)}", "error": "TEST_EXCEPTION"}
            )


class SystemDiagnostics:
    """System-wide diagnostic tools."""

    @staticmethod
    async def run_auth_diagnostics() -> List[DiagnosticResult]:
        """Run all authentication-related diagnostics."""
        diagnostics = [
            AuthDiagnostics.validate_jwt_secret(),
            await AuthDiagnostics.test_supabase_connection(),
            await AuthDiagnostics.test_service_role_permissions(),
        ]

        return diagnostics

    @staticmethod
    async def health_check() -> Dict[str, Any]:
        """Complete system health check."""
        start_time = time.time()
        results = await SystemDiagnostics.run_auth_diagnostics()

        health_status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_status": "healthy" if all(r.passed for r in results) else "unhealthy",
            "duration_ms": (time.time() - start_time) * 1000,
            "checks": [
                {
                    "name": r.name,
                    "status": "pass" if r.passed else "fail",
                    "details": r.details,
                    "timestamp": r.timestamp
                }
                for r in results
            ]
        }

        return health_status


def create_test_jwt(user_id: Optional[str] = None, exp_minutes: int = 60) -> str:
    """Create a test JWT for development/testing purposes."""
    payload = {
        "sub": user_id or str(uuid.uuid4()),
        "exp": int(time.time()) + (exp_minutes * 60),
        "iat": int(time.time()),
        "iss": f"{settings.SUPABASE_URL}/auth/v1",
        "aud": "authenticated",
        "role": "authenticated"
    }

    return pyjwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")


async def debug_account_deletion(user_id: str) -> Dict[str, Any]:
    """Debug account deletion process for a specific user."""
    debug_info = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "steps": []
    }

    # Step 1: Validate configuration
    jwt_check = AuthDiagnostics.validate_jwt_secret()
    debug_info["steps"].append({
        "step": "jwt_validation",
        "passed": jwt_check.passed,
        "details": jwt_check.details
    })

    # Step 2: Test Supabase connectivity
    conn_check = await AuthDiagnostics.test_supabase_connection()
    debug_info["steps"].append({
        "step": "supabase_connection",
        "passed": conn_check.passed,
        "details": conn_check.details
    })

    # Step 3: Test service role permissions
    perm_check = await AuthDiagnostics.test_service_role_permissions()
    debug_info["steps"].append({
        "step": "service_role_permissions",
        "passed": perm_check.passed,
        "details": perm_check.details
    })

    # Step 4: Test actual deletion endpoint (dry run)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(  # GET instead of DELETE for dry run
                f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                },
                timeout=10
            )

            debug_info["steps"].append({
                "step": "user_lookup",
                "passed": response.status_code == 200,
                "details": {
                    "status_code": response.status_code,
                    "user_exists": response.status_code == 200,
                    "response_preview": response.text[:200] if response.status_code != 200 else "User found"
                }
            })

    except Exception as e:
        debug_info["steps"].append({
            "step": "user_lookup",
            "passed": False,
            "details": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        })

    debug_info["overall_status"] = "ready" if all(step["passed"] for step in debug_info["steps"]) else "issues_found"

    return debug_info