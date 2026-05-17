"""Tenant-scoped approval action endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.services.approval_service import (
    approve_action,
    get_approvals,
    reject_action,
)
from app.services.audit_service import write_audit_log


class ApprovalResponse(BaseModel):
    id: UUID
    action_type: str
    action_payload: dict | None
    reasoning: str | None
    data_sources: dict | None
    expected_outcome: str | None
    status: str
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    rejection_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RejectRequest(BaseModel):
    reason: str


router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=list[ApprovalResponse])
async def list_approvals(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List approval actions for the authenticated tenant."""
    return await get_approvals(
        db,
        tenant_id=user["tenant_id"],
        status_filter=status,
        limit=limit,
        offset=offset,
    )


@router.post("/{action_id}/approve", response_model=ApprovalResponse)
async def approve(
    action_id: UUID,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending action."""
    action = await approve_action(
        db,
        tenant_id=user["tenant_id"],
        action_id=action_id,
        reviewer_id=user["user_id"],
    )
    if not action:
        raise HTTPException(status_code=404, detail="Pending action not found")

    await write_audit_log(
        db=db,
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        action_type="approval.approve",
        action_detail={"action_id": str(action_id), "action_type": action.action_type},
        outcome="success",
        ip_address=request.client.host if request.client else None,
    )
    return action


@router.post("/{action_id}/reject", response_model=ApprovalResponse)
async def reject(
    action_id: UUID,
    body: RejectRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending action with a reason."""
    action = await reject_action(
        db,
        tenant_id=user["tenant_id"],
        action_id=action_id,
        reviewer_id=user["user_id"],
        reason=body.reason,
    )
    if not action:
        raise HTTPException(status_code=404, detail="Pending action not found")

    await write_audit_log(
        db=db,
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        action_type="approval.reject",
        action_detail={
            "action_id": str(action_id),
            "action_type": action.action_type,
            "reason": body.reason,
        },
        outcome="success",
        ip_address=request.client.host if request.client else None,
    )
    return action
