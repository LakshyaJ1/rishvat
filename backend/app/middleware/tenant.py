"""
AI CFO — Tenant Scoping Middleware

Extracts tenant_id from the JWT token and makes it available
to every request handler via request.state.tenant_id.

This is the primary application-level tenant isolation mechanism.
Combined with PostgreSQL RLS for defense-in-depth.
"""

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import decode_token
from app.db.rls import set_tenant_context
from app.db.session import get_db

logger = logging.getLogger(__name__)

# Bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    FastAPI dependency that extracts and validates the JWT token.
    Returns user context dict with user_id, tenant_id, and role.
    Sets request.state for downstream use.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "AUTH_REQUIRED", "message": "Authentication required"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid or expired token"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_context = {
        "user_id": UUID(payload["sub"]),
        "tenant_id": UUID(payload["tenant_id"]),
        "role": payload.get("role", "founder"),
    }

    # Make tenant_id available on request state for middleware/logging
    request.state.user_id = user_context["user_id"]
    request.state.tenant_id = user_context["tenant_id"]
    request.state.role = user_context["role"]

    # Bind this DB transaction to the authenticated tenant so PostgreSQL RLS
    # enforces the same scope as the application layer.
    await set_tenant_context(db, user_context["tenant_id"])

    return user_context


async def require_tenant(
    user: dict = Depends(get_current_user),
) -> UUID:
    """
    Dependency that returns just the tenant_id.
    Use this for endpoints that only need tenant scoping.
    """
    return user["tenant_id"]
