"""Tenant-scoped notification endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.services.notification_service import (
    dismiss_notification,
    get_notifications,
    mark_read,
)
from app.services.audit_service import write_audit_log


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    severity: str
    title: str
    body: str | None
    data: dict | None
    read: bool
    dismissed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the authenticated tenant."""
    return await get_notifications(
        db,
        tenant_id=user["tenant_id"],
        type_filter=type,
        severity_filter=severity,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.post("/{notification_id}/read")
async def read_notification(
    notification_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    success = await mark_read(db, user["tenant_id"], notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    await write_audit_log(
        db=db,
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        action_type="notification.read",
        action_detail={"notification_id": str(notification_id)},
        outcome="success",
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "ok"}


@router.post("/{notification_id}/dismiss")
async def dismiss(
    notification_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dismiss a notification."""
    success = await dismiss_notification(db, user["tenant_id"], notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    await write_audit_log(
        db=db,
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        action_type="notification.dismiss",
        action_detail={"notification_id": str(notification_id)},
        outcome="success",
        ip_address=request.client.host if request.client else None,
    )
    return {"status": "ok"}
