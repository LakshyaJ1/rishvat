"""
AI CFO — Tenant Service

Business logic for tenant management.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


async def get_tenant(db: AsyncSession, tenant_id: UUID) -> Tenant | None:
    """Fetch a tenant by ID."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def get_tenant_by_slug(db: AsyncSession, slug: str) -> Tenant | None:
    """Fetch a tenant by slug."""
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return result.scalar_one_or_none()


async def update_autopilot_level(
    db: AsyncSession, tenant_id: UUID, level: str
) -> Tenant:
    """Update a tenant's autopilot level."""
    if level not in ("advisory", "semi_auto", "full_auto"):
        raise ValueError(f"Invalid autopilot level: {level}")

    tenant = await get_tenant(db, tenant_id)
    if not tenant:
        raise ValueError("Tenant not found")

    tenant.autopilot_level = level
    await db.flush()

    logger.info(f"Tenant {tenant_id} autopilot level set to {level}")
    return tenant
