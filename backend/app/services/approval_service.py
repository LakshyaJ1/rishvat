"""AI CFO — Approval Service

Creates, queries, approves, and rejects approval actions.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_action import ApprovalAction


async def create_approval(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    action_type: str,
    action_payload: dict | None = None,
    reasoning: str | None = None,
    data_sources: dict | None = None,
    expected_outcome: str | None = None,
) -> ApprovalAction:
    """Create a new pending approval action."""
    action = ApprovalAction(
        tenant_id=tenant_id,
        action_type=action_type,
        action_payload=action_payload,
        reasoning=reasoning,
        data_sources=data_sources,
        expected_outcome=expected_outcome,
    )
    db.add(action)
    await db.flush()
    return action


async def get_approvals(
    db: AsyncSession,
    tenant_id: UUID,
    *,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ApprovalAction]:
    """Get paginated approvals for a tenant."""
    query = (
        select(ApprovalAction)
        .where(ApprovalAction.tenant_id == tenant_id)
    )
    if status_filter:
        query = query.where(ApprovalAction.status == status_filter)
    query = query.order_by(ApprovalAction.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def approve_action(
    db: AsyncSession,
    tenant_id: UUID,
    action_id: UUID,
    reviewer_id: UUID,
) -> ApprovalAction | None:
    """Approve a pending action."""
    result = await db.execute(
        select(ApprovalAction)
        .where(
            ApprovalAction.id == action_id,
            ApprovalAction.tenant_id == tenant_id,
            ApprovalAction.status == "pending",
        )
    )
    action = result.scalar_one_or_none()
    if not action:
        return None

    action.status = "approved"
    action.reviewed_by = reviewer_id
    action.reviewed_at = datetime.now(timezone.utc)
    await db.flush()
    return action


async def reject_action(
    db: AsyncSession,
    tenant_id: UUID,
    action_id: UUID,
    reviewer_id: UUID,
    reason: str,
) -> ApprovalAction | None:
    """Reject a pending action with a reason."""
    result = await db.execute(
        select(ApprovalAction)
        .where(
            ApprovalAction.id == action_id,
            ApprovalAction.tenant_id == tenant_id,
            ApprovalAction.status == "pending",
        )
    )
    action = result.scalar_one_or_none()
    if not action:
        return None

    action.status = "rejected"
    action.reviewed_by = reviewer_id
    action.reviewed_at = datetime.now(timezone.utc)
    action.rejection_reason = reason
    await db.flush()
    return action
