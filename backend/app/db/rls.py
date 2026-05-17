"""
AI CFO — Row-Level Security Helpers

Utilities for setting and managing PostgreSQL RLS context.
Every request sets the current tenant_id in the database session
so RLS policies can enforce tenant isolation at the database level.
"""

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, tenant_id: UUID) -> None:
    """
    Set the current tenant_id in the PostgreSQL session.
    This is used by RLS policies to filter rows automatically.
    Must be called at the start of every tenant-scoped request.
    """
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def clear_tenant_context(session: AsyncSession) -> None:
    """Clear the tenant context (used in tests and admin operations)."""
    await session.execute(text("RESET app.current_tenant_id"))
