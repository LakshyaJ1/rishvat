"""
AI CFO — Auth Service

Business logic for registration, login, and token refresh.
Handles tenant creation on registration and audit log writes.
"""

import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User


def _slugify(name: str) -> str:
    """Convert a company name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


async def register_user(
    db: AsyncSession,
    request: RegisterRequest,
    ip_address: str | None = None,
) -> AuthResponse:
    """
    Register a new user and create their tenant.
    This is the primary onboarding entry point.
    """
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise ValueError("A user with this email already exists")

    # Create tenant
    slug = _slugify(request.company_name)

    # Ensure slug uniqueness
    existing_tenant = await db.execute(select(Tenant).where(Tenant.slug == slug))
    if existing_tenant.scalar_one_or_none():
        # Append a short suffix for uniqueness
        import uuid as _uuid
        slug = f"{slug}-{str(_uuid.uuid4())[:8]}"

    tenant = Tenant(
        name=request.company_name,
        slug=slug,
        jurisdiction=request.jurisdiction,
    )
    db.add(tenant)
    await db.flush()  # Get tenant.id without committing

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        role="founder",
        tenant_id=tenant.id,
    )
    db.add(user)
    await db.flush()

    # Generate tokens
    access_token = create_access_token(user.id, tenant.id, user.role)
    refresh_token = create_refresh_token(user.id, tenant.id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            tenant_id=tenant.id,
        ),
    )


async def login_user(
    db: AsyncSession,
    request: LoginRequest,
    ip_address: str | None = None,
) -> AuthResponse:
    """Authenticate user and return tokens."""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("Account is deactivated")

    access_token = create_access_token(user.id, user.tenant_id, user.role)
    refresh_token = create_refresh_token(user.id, user.tenant_id)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            tenant_id=user.tenant_id,
        ),
    )


async def refresh_tokens(
    db: AsyncSession,
    request: RefreshRequest,
) -> TokenResponse:
    """Refresh access and refresh tokens using a valid refresh token."""
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    user_id = UUID(payload["sub"])
    tenant_id = UUID(payload["tenant_id"])

    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise ValueError("User not found or deactivated")

    access_token = create_access_token(user.id, user.tenant_id, user.role)
    new_refresh_token = create_refresh_token(user.id, user.tenant_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
