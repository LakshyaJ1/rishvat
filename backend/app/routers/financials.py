"""Tenant-scoped deterministic financial metric endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.tenant import get_current_user
from app.schemas.financial import (
    ARRResult,
    BurnRateResult,
    CACResult,
    ChurnResult,
    FinancialSnapshotResponse,
    MRRResult,
    NRRResult,
    RunwayResult,
)
from app.services.financial_service import (
    get_arr_for_tenant,
    get_burn_rate_for_tenant,
    get_cac_for_tenant,
    get_churn_for_tenant,
    get_mrr_for_tenant,
    get_nrr_for_tenant,
    get_runway_for_tenant,
    get_snapshot_for_tenant,
)

router = APIRouter(prefix="/financials", tags=["financials"])


@router.get("/burn", response_model=BurnRateResult)
async def get_burn_rate(
    period_months: int = Query(default=3, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return current tenant burn rate from normalized financial records."""
    return await get_burn_rate_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        period_months=period_months,
    )


@router.get("/runway", response_model=RunwayResult)
async def get_runway(
    cash_balance_cents: int = Query(ge=0),
    period_months: int = Query(default=3, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return runway from current cash balance and trailing net burn."""
    return await get_runway_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        cash_balance_cents=cash_balance_cents,
        period_months=period_months,
    )


@router.get("/snapshot", response_model=FinancialSnapshotResponse)
async def get_snapshot(
    cash_balance_cents: int | None = Query(default=None, ge=0),
    period_months: int = Query(default=3, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the Stage 1 financial snapshot contract for dashboard and AI use."""
    return await get_snapshot_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        cash_balance_cents=cash_balance_cents,
        period_months=period_months,
    )


@router.get("/mrr", response_model=MRRResult)
async def get_mrr(
    period_months: int = Query(default=1, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return trailing monthly recurring revenue approximation."""
    return await get_mrr_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        period_months=period_months,
    )


@router.get("/arr", response_model=ARRResult)
async def get_arr(
    period_months: int = Query(default=1, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return ARR derived from trailing MRR."""
    return await get_arr_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        period_months=period_months,
    )


@router.get("/cac", response_model=CACResult)
async def get_cac(
    new_customers: int = Query(ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return customer acquisition cost from sales and marketing spend."""
    return await get_cac_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        new_customers=new_customers,
    )


@router.get("/churn", response_model=ChurnResult)
async def get_churn(
    period_months: int = Query(default=1, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return churn contract with explicit insufficiency when data is missing."""
    return await get_churn_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        period_months=period_months,
    )


@router.get("/nrr", response_model=NRRResult)
async def get_nrr(
    period_months: int = Query(default=1, ge=1, le=24),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return NRR contract with explicit insufficiency when data is missing."""
    return await get_nrr_for_tenant(
        db=db,
        tenant_id=user["tenant_id"],
        period_months=period_months,
    )
