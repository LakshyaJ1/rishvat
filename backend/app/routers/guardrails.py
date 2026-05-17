"""Guardrails validation endpoint for local AI integration."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.guardrails.engine import validate_ai_output
from app.guardrails.schemas import GuardrailInput, GuardrailResult, GuardrailValidateRequest
from app.middleware.tenant import get_current_user
from app.models.tenant import Tenant
from app.services.approval_service import create_approval
from app.services.audit_service import write_audit_log
from app.services.autopilot_service import get_autopilot_config_for_category
from app.services.financial_service import get_mrr_for_tenant

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


ACTION_CATEGORY_MAP = {
    "payment": "payment",
    "wire_transfer": "payment",
    "refund_issue": "payment",
    "pricing_change": "pricing",
    "pricing_change_existing_customers": "pricing",
    "price_increase_existing_customers": "pricing",
    "report": "reporting",
    "report_send": "reporting",
    "recommendation": "reporting",
    "alert": "alerts",
    "categorization": "categorization",
}


def _category_for_action(payload: GuardrailValidateRequest) -> str:
    if payload.category:
        return payload.category
    return ACTION_CATEGORY_MAP.get(payload.action_type, "alerts")


@router.post("/validate", response_model=GuardrailResult)
async def validate_guardrails(
    payload: GuardrailValidateRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate AI output/action against deterministic guardrails."""
    tenant_id = user["tenant_id"]
    category = _category_for_action(payload)
    config = await get_autopilot_config_for_category(db, tenant_id, category)
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    mrr = await get_mrr_for_tenant(db, tenant_id)

    scoped_payload = GuardrailInput(
        tenant_id=tenant_id,
        **payload.model_dump(exclude={"reasoning", "expected_outcome"}),
    )
    scoped_payload.category = category
    if config:
        scoped_payload.requested_autonomy_level = config.autonomy_level

    result = validate_ai_output(
        scoped_payload,
        max_amount_cents=config.max_amount_cents if config else 0,
        revenue_floor_cents=config.revenue_floor_cents if config else 0,
        current_revenue_cents=mrr.mrr_cents,
        jurisdiction=tenant.jurisdiction if tenant else "US",
        category_locked=config.locked if config else False,
    )

    approval_action = None
    if result.approved and result.requires_human_approval:
        approval_action = await create_approval(
            db,
            tenant_id=tenant_id,
            action_type=scoped_payload.action_type,
            action_payload=result.modified_output,
            reasoning=payload.reasoning or result.reason,
            data_sources={"sources": scoped_payload.data_sources},
            expected_outcome=payload.expected_outcome,
        )
        result = result.model_copy(update={"approval_action_id": approval_action.id})

    await write_audit_log(
        db=db,
        tenant_id=tenant_id,
        user_id=user["user_id"],
        action_type="guardrail.validate",
        action_detail={
            "action_type": scoped_payload.action_type,
            "approved": result.approved,
            "requires_human_approval": result.requires_human_approval,
            "approval_action_id": str(approval_action.id) if approval_action else None,
            "category": category,
            "autonomy_level": scoped_payload.requested_autonomy_level,
            "violations": result.violations,
            "warnings": result.warnings,
        },
        data_sources={"sources": scoped_payload.data_sources},
        outcome="success" if result.approved else "blocked",
        ip_address=request.client.host if request.client else None,
    )
    return result
