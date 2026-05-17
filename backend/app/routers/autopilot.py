"""Tenant-scoped autopilot configuration endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.services.audit_service import write_audit_log
from app.services.autopilot_service import get_autopilot_configs, upsert_autopilot_config


VALID_CATEGORIES = {"payment", "pricing", "reporting", "categorization", "alerts"}
VALID_AUTONOMY_LEVELS = {"advisory", "semi_auto", "full_auto"}


class AutopilotConfigRequest(BaseModel):
    category: str
    autonomy_level: str = "advisory"
    max_amount_cents: int = Field(default=0, ge=0)
    revenue_floor_cents: int = Field(default=0, ge=0)
    locked: bool = False


class AutopilotConfigResponse(BaseModel):
    id: UUID
    category: str
    autonomy_level: str
    max_amount_cents: int
    revenue_floor_cents: int
    locked: bool

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/autopilot", tags=["autopilot"])


@router.get("/config", response_model=list[AutopilotConfigResponse])
async def list_autopilot_configs(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all autopilot configurations for the authenticated tenant."""
    return await get_autopilot_configs(db, tenant_id=user["tenant_id"])


@router.post("/configure", response_model=AutopilotConfigResponse)
async def configure_autopilot(
    payload: AutopilotConfigRequest,
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update autopilot configuration for a category."""
    from fastapi import HTTPException

    if payload.category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid category. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
        )
    if payload.autonomy_level not in VALID_AUTONOMY_LEVELS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid autonomy level. Must be one of: {', '.join(sorted(VALID_AUTONOMY_LEVELS))}",
        )

    config = await upsert_autopilot_config(
        db,
        tenant_id=user["tenant_id"],
        category=payload.category,
        autonomy_level=payload.autonomy_level,
        max_amount_cents=payload.max_amount_cents,
        revenue_floor_cents=payload.revenue_floor_cents,
        locked=payload.locked,
    )

    await write_audit_log(
        db=db,
        tenant_id=user["tenant_id"],
        user_id=user["user_id"],
        action_type="autopilot.configure",
        action_detail={
            "category": payload.category,
            "autonomy_level": payload.autonomy_level,
            "max_amount_cents": payload.max_amount_cents,
            "locked": payload.locked,
        },
        outcome="success",
        ip_address=request.client.host if request.client else None,
    )
    return config
