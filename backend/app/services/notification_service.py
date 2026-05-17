"""AI CFO — Notification Service

Creates, queries, and manages tenant-scoped notifications.
"""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    type: str,
    severity: str,
    title: str,
    body: str | None = None,
    data: dict | None = None,
) -> Notification:
    """Create a new notification for a tenant."""
    notification = Notification(
        tenant_id=tenant_id,
        type=type,
        severity=severity,
        title=title,
        body=body,
        data=data,
    )
    db.add(notification)
    await db.flush()
    return notification


async def get_notifications(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    type_filter: str | None = None,
    severity_filter: str | None = None,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Notification]:
    """Get paginated notifications for a tenant."""
    query = (
        select(Notification)
        .where(Notification.tenant_id == tenant_id)
        .where(Notification.dismissed == False)  # noqa: E712
    )
    if type_filter:
        query = query.where(Notification.type == type_filter)
    if severity_filter:
        query = query.where(Notification.severity == severity_filter)
    if unread_only:
        query = query.where(Notification.read == False)  # noqa: E712

    query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, tenant_id: UUID, notification_id: UUID) -> bool:
    """Mark a notification as read."""
    result = await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.tenant_id == tenant_id)
        .values(read=True)
    )
    await db.flush()
    return result.rowcount > 0


async def dismiss_notification(db: AsyncSession, tenant_id: UUID, notification_id: UUID) -> bool:
    """Dismiss a notification (hide from default list)."""
    result = await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.tenant_id == tenant_id)
        .values(dismissed=True)
    )
    await db.flush()
    return result.rowcount > 0
