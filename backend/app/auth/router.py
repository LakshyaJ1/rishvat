"""
AI CFO — Auth Router

Endpoints: register, login, refresh.
All responses follow the standard error contract.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import login_user, refresh_tokens, register_user
from app.db.session import get_db
from app.services.audit_service import write_audit_log

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and create a tenant",
)
async def register(
    request: RegisterRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new tenant and founding user.
    Returns JWT tokens for immediate authentication.
    """
    try:
        result = await register_user(
            db,
            request,
            ip_address=http_request.client.host if http_request.client else None,
        )

        # Audit log: registration
        await write_audit_log(
            db=db,
            tenant_id=result.user.tenant_id,
            user_id=result.user.id,
            action_type="auth.register",
            action_detail={"email": request.email, "company": request.company_name},
            outcome="success",
            ip_address=http_request.client.host if http_request.client else None,
        )

        logger.info(f"New tenant registered: {request.company_name} ({request.email})")
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "REGISTRATION_ERROR", "message": str(e)}},
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Registration failed"}},
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens."""
    try:
        result = await login_user(
            db,
            request,
            ip_address=http_request.client.host if http_request.client else None,
        )

        # Audit log: login
        await write_audit_log(
            db=db,
            tenant_id=result.user.tenant_id,
            user_id=result.user.id,
            action_type="auth.login",
            action_detail={"email": request.email},
            outcome="success",
            ip_address=http_request.client.host if http_request.client else None,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "AUTH_ERROR", "message": str(e)}},
        )
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_ERROR", "message": "Login failed"}},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Exchange a valid refresh token for new access and refresh tokens."""
    try:
        return await refresh_tokens(db, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_ERROR", "message": str(e)}},
        )
