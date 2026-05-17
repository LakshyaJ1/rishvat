"""AI CFO — Autopilot Config Service

CRUD operations for per-category autopilot configurations.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autopilot_config import AutopilotConfig


async def get_autopilot_configs(
    db: AsyncSession,
    tenant_id: UUID,
) -> list[AutopilotConfig]:
    """Get all autopilot configs for a tenant."""
    result = await db.execute(
        select(AutopilotConfig)
        .where(AutopilotConfig.tenant_id == tenant_id)
        .order_by(AutopilotConfig.category)
    )
    return list(result.scalars().all())


async def get_autopilot_config_for_category(
    db: AsyncSession,
    tenant_id: UUID,
    category: str,
) -> AutopilotConfig | None:
    """Get autopilot config for a specific category."""
    result = await db.execute(
        select(AutopilotConfig)
        .where(
            AutopilotConfig.tenant_id == tenant_id,
            AutopilotConfig.category == category,
        )
    )
    return result.scalar_one_or_none()


async def upsert_autopilot_config(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    category: str,
    autonomy_level: str = "advisory",
    max_amount_cents: int = 0,
    revenue_floor_cents: int = 0,
    locked: bool = False,
) -> AutopilotConfig:
    """Create or update an autopilot config for a category."""
    existing = await get_autopilot_config_for_category(db, tenant_id, category)

    if existing:
        existing.autonomy_level = autonomy_level
        existing.max_amount_cents = max_amount_cents
        existing.revenue_floor_cents = revenue_floor_cents
        existing.locked = locked
        await db.flush()
        return existing

    config = AutopilotConfig(
        tenant_id=tenant_id,
        category=category,
        autonomy_level=autonomy_level,
        max_amount_cents=max_amount_cents,
        revenue_floor_cents=revenue_floor_cents,
        locked=locked,
    )
    db.add(config)
    await db.flush()
    return config
