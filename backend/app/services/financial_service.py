"""Tenant-scoped financial query and metric service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.financials.calculations import (
    compute_arr,
    compute_burn_rate,
    compute_cac,
    compute_churn_rate,
    compute_mrr,
    compute_nrr,
    compute_runway,
)
from app.models.financial_record import FinancialRecord
from app.schemas.financial import FinancialSnapshotResponse


async def get_financial_records_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
) -> list[FinancialRecord]:
    """Load all normalized financial records for one tenant."""
    result = await db.execute(
        select(FinancialRecord)
        .where(FinancialRecord.tenant_id == tenant_id)
        .order_by(FinancialRecord.occurred_at.desc())
    )
    return list(result.scalars().all())


async def get_burn_rate_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    period_months: int = 3,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_burn_rate(records, period_months=period_months)


async def get_runway_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    cash_balance_cents: int,
    period_months: int = 3,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_runway(
        records,
        cash_balance_cents=cash_balance_cents,
        period_months=period_months,
    )


async def get_mrr_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    period_months: int = 1,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_mrr(records, period_months=period_months)


async def get_arr_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    period_months: int = 1,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_arr(compute_mrr(records, period_months=period_months))


async def get_cac_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    new_customers: int,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_cac(records, new_customers=new_customers)


async def get_churn_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    period_months: int = 1,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_churn_rate(records, period_months=period_months)


async def get_nrr_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    period_months: int = 1,
):
    records = await get_financial_records_for_tenant(db, tenant_id)
    return compute_nrr(records, period_months=period_months)


async def get_snapshot_for_tenant(
    db: AsyncSession,
    tenant_id: UUID,
    cash_balance_cents: int | None = None,
    period_months: int = 3,
) -> FinancialSnapshotResponse:
    records = await get_financial_records_for_tenant(db, tenant_id)
    burn_rate = compute_burn_rate(records, period_months=period_months)
    mrr = compute_mrr(records)
    arr = compute_arr(mrr)
    runway = (
        compute_runway(records, cash_balance_cents, period_months=period_months)
        if cash_balance_cents is not None
        else None
    )
    return FinancialSnapshotResponse(
        burn_rate=burn_rate,
        runway=runway,
        mrr=mrr,
        arr=arr,
        record_count=len(records),
    )
