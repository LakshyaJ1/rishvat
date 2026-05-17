"""
AI CFO — Audit Log Router

Endpoint for reading the audit log (tenant-scoped).
This is read-only — the audit service is the only writer.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit-log", tags=["audit"])


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="Get tenant audit log",
)
async def get_audit_log(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    action_type: str | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns paginated audit log entries for the current tenant.
    Optionally filter by action_type.
    """
    tenant_id = user["tenant_id"]
    offset = (page - 1) * per_page

    # Build query with tenant scoping
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)
    count_query = select(func.count(AuditLog.id)).where(
        AuditLog.tenant_id == tenant_id
    )

    if action_type:
        query = query.where(AuditLog.action_type == action_type)
        count_query = count_query.where(AuditLog.action_type == action_type)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    entries = result.scalars().all()

    items = [AuditLogResponse.model_validate(entry) for entry in entries]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )
