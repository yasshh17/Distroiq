import asyncio
import uuid
from typing import Annotated, Dict, Any, Optional
from datetime import datetime

import httpx
from fastapi import APIRouter, Header, HTTPException, status, Request
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import AuthError, extract_user_id, verify_jwt
from app.core.audit import (
    AuditLogger, AuditAction, AuditOutcome, AuditContext,
    audit_account_deletion_attempt, audit_unauthorized_access
)
from app.core.logging import log_context, auth_logger, security_logger
from app.core.diagnostics import debug_account_deletion
from app.core.errors import (
    AuthenticationError, account_deletion_not_configured,
    account_not_found, account_deletion_failed, ExternalServiceError
)

router = APIRouter(prefix="/auth", tags=["auth"])


class AccountDeletionRequest(BaseModel):
    confirmation: str
    reason: Optional[str] = None


class AccountDeletionResponse(BaseModel):
    message: str
    user_id: str
    timestamp: str
    audit_id: str


def _extract_client_info(request: Request) -> Dict[str, Any]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
        "forwarded_for": request.headers.get("x-forwarded-for"),
    }


def _require_user(authorization: str | None, request: Request) -> uuid.UUID:
    client_info = _extract_client_info(request)

    if not authorization or not authorization.lower().startswith("bearer "):
        audit_unauthorized_access(
            endpoint="/auth/account",
            ip_address=client_info["ip_address"] or "unknown",
            user_agent=client_info["user_agent"] or "unknown",
            reason="missing_authorization_header"
        )

        raise AuthenticationError(
            message="Authorization header required. Provide a valid Bearer token.",
            code="MISSING_AUTH_HEADER"
        )

    token = authorization[len("bearer "):].strip()

    try:
        payload = verify_jwt(token)
        user_id = extract_user_id(payload)

        AuditLogger.log_auth_event(
            action=AuditAction.TOKEN_REFRESH,
            outcome=AuditOutcome.SUCCESS,
            user_id=str(user_id),
            ip_address=client_info["ip_address"],
            details={"endpoint": "/auth/account", "token_type": "bearer"}
        )

        return user_id

    except AuthError as exc:
        audit_unauthorized_access(
            endpoint="/auth/account",
            ip_address=client_info["ip_address"] or "unknown",
            user_agent=client_info["user_agent"] or "unknown",
            reason=f"jwt_verification_failed: {str(exc)}"
        )

        AuditLogger.log_auth_event(
            action=AuditAction.LOGIN_FAILURE,
            outcome=AuditOutcome.FAILURE,
            ip_address=client_info["ip_address"],
            details={"endpoint": "/auth/account", "error": str(exc)},
            error_message=str(exc)
        )

        raise AuthenticationError(
            message=f"Token verification failed: {str(exc)}",
            code="TOKEN_VERIFICATION_FAILED"
        )


async def _validate_service_role_config() -> None:
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        security_logger.error(
            "Account deletion attempted without service role key configured",
            extra={
                "error_type": "configuration_error",
                "component": "auth.account_deletion",
                "environment": settings.APP_ENV
            }
        )

        account_deletion_not_configured()


async def _delete_user_from_supabase(user_id: str, client_info: Dict[str, Any]) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            check_resp = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                },
            )

            if check_resp.status_code == 404:
                auth_logger.warning(
                    f"Attempted to delete non-existent user: {user_id}",
                    extra={"user_id": user_id, "status_code": 404}
                )

                account_not_found(user_id)

            if check_resp.status_code != 200:
                raise ExternalServiceError(
                    message=f"Unable to verify user account. Service returned {check_resp.status_code}",
                    service_name="Supabase",
                    code="USER_VERIFICATION_FAILED"
                )

            delete_resp = await client.delete(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users/{user_id}",
                headers={
                    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                },
            )

            if delete_resp.status_code not in (200, 204):
                error_detail = f"Supabase deletion failed with status {delete_resp.status_code}"

                if delete_resp.status_code == 401:
                    error_detail = "Service role authentication failed. Invalid credentials."
                elif delete_resp.status_code == 403:
                    error_detail = "Service role lacks permission to delete users."
                elif delete_resp.status_code == 429:
                    error_detail = "Rate limit exceeded. Please try again later."

                AuditLogger.log_account_deletion(
                    user_id=user_id,
                    outcome=AuditOutcome.FAILURE,
                    ip_address=client_info["ip_address"],
                    error_message=error_detail,
                    details={
                        "supabase_status_code": delete_resp.status_code,
                        "supabase_response": delete_resp.text[:200]
                    }
                )

                account_deletion_failed(user_id, error_detail)

        except httpx.TimeoutException:
            error_msg = "Request to Supabase timed out. Please try again."

            AuditLogger.log_account_deletion(
                user_id=user_id,
                outcome=AuditOutcome.FAILURE,
                ip_address=client_info["ip_address"],
                error_message=error_msg,
                details={"error_type": "timeout"}
            )

            raise ExternalServiceError(
                message=error_msg,
                service_name="Supabase",
                code="SERVICE_TIMEOUT"
            )

        except httpx.RequestError as e:
            error_msg = f"Network error communicating with Supabase: {str(e)}"

            AuditLogger.log_account_deletion(
                user_id=user_id,
                outcome=AuditOutcome.FAILURE,
                ip_address=client_info["ip_address"],
                error_message=error_msg,
                details={"error_type": "network_error", "exception": str(e)}
            )

            raise ExternalServiceError(
                message="Unable to reach authentication service. Please try again later.",
                service_name="Supabase",
                code="NETWORK_ERROR",
                upstream_error=str(e)
            )


@router.delete("/account")
async def delete_account(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AccountDeletionResponse:
    correlation_id = str(uuid.uuid4())[:8]

    with log_context(correlation_id):
        auth_logger.info(
            "Account deletion request received",
            extra={"correlation_id": correlation_id, "endpoint": "/auth/account"}
        )

        client_info = _extract_client_info(request)
        user_id = _require_user(authorization, request)
        user_id_str = str(user_id)

        with AuditContext(correlation_id) as audit_ctx:
            try:
                audit_ctx.log_event(
                    action=AuditAction.ACCOUNT_DELETE_ATTEMPT,
                    outcome=AuditOutcome.SUCCESS,  # Attempt started successfully
                    user_id=user_id_str,
                    ip_address=client_info["ip_address"],
                    resource_type="user_account",
                    resource_id=user_id_str,
                    details={
                        "user_agent": client_info["user_agent"],
                        "deletion_method": "api_endpoint",
                        "confirmation_required": False
                    }
                )

                await _validate_service_role_config()
                await _delete_user_from_supabase(user_id_str, client_info)

                timestamp = datetime.utcnow().isoformat() + "Z"
                audit_id = str(uuid.uuid4())

                AuditLogger.log_account_deletion(
                    user_id=user_id_str,
                    outcome=AuditOutcome.SUCCESS,
                    ip_address=client_info["ip_address"],
                    details={
                        "correlation_id": correlation_id,
                        "deletion_timestamp": timestamp,
                        "cleanup_completed": True
                    }
                )

                auth_logger.info(
                    f"Account successfully deleted for user {user_id_str}",
                    extra={
                        "user_id": user_id_str,
                        "correlation_id": correlation_id,
                        "audit_id": audit_id
                    }
                )

                return AccountDeletionResponse(
                    message="Account successfully deleted",
                    user_id=user_id_str,
                    timestamp=timestamp,
                    audit_id=audit_id
                )

            except HTTPException:
                raise

            except Exception as e:
                error_msg = f"Unexpected error during account deletion: {str(e)}"

                AuditLogger.log_account_deletion(
                    user_id=user_id_str,
                    outcome=AuditOutcome.FAILURE,
                    ip_address=client_info["ip_address"],
                    error_message=error_msg,
                    details={
                        "correlation_id": correlation_id,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e)
                    }
                )

                security_logger.error(
                    "Unexpected error in account deletion",
                    extra={
                        "user_id": user_id_str,
                        "correlation_id": correlation_id,
                        "exception": str(e),
                        "exception_type": type(e).__name__
                    },
                    exc_info=True
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred. Support has been notified.",
                )


@router.get("/account/deletion-debug/{user_id}")
async def debug_account_deletion_endpoint(
    user_id: str,
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> Dict[str, Any]:
    if settings.APP_ENV == "production":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug endpoints not available in production"
        )

    _ = _require_user(authorization, request)

    return await debug_account_deletion(user_id)
