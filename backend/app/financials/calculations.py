"""Deterministic financial metric calculations.

These functions are pure Python and deliberately contain no AI calls. They are
the stable backend contract used by the API layer and the local AI layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.financial_record import FinancialRecord
from app.schemas.financial import (
    ARRResult,
    BurnRateResult,
    CACResult,
    ChurnResult,
    MRRResult,
    NRRResult,
    RunwayResult,
)


REVENUE_TYPES = {"revenue"}
EXPENSE_TYPES = {"expense", "fee"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _period_start(period_months: int, period_end: datetime | None = None) -> datetime:
    if period_months < 1:
        raise ValueError("period_months must be >= 1")
    end = period_end or _utc_now()
    return end - timedelta(days=30 * period_months)


def _records_in_period(
    records: list[FinancialRecord],
    period_months: int,
    period_end: datetime | None = None,
) -> tuple[list[FinancialRecord], datetime, datetime]:
    end = period_end or _utc_now()
    start = _period_start(period_months, end)
    scoped = [
        record
        for record in records
        if start <= _ensure_aware(record.occurred_at) <= end
    ]
    return scoped, start, end


def _record_ids(records: list[FinancialRecord]) -> list[UUID]:
    return [record.id for record in records if record.id is not None]


def compute_burn_rate(
    records: list[FinancialRecord],
    period_months: int = 3,
    period_end: datetime | None = None,
) -> BurnRateResult:
    """Compute gross and net monthly burn over a trailing period.

    Gross burn is operating outflow only. Net burn subtracts inflows from
    outflows and floors at zero, because negative burn means the company was
    cash-flow positive for the period.
    """
    scoped, start, end = _records_in_period(records, period_months, period_end)

    expense_records = [
        record
        for record in scoped
        if record.record_type in EXPENSE_TYPES and record.amount_cents < 0
    ]
    revenue_records = [
        record
        for record in scoped
        if record.record_type in REVENUE_TYPES and record.amount_cents > 0
    ]

    expense_cents = sum(abs(record.amount_cents) for record in expense_records)
    revenue_cents = sum(record.amount_cents for record in revenue_records)
    gross_burn_rate_cents = round(expense_cents / period_months)
    net_burn_total_cents = max(expense_cents - revenue_cents, 0)
    net_burn_rate_cents = round(net_burn_total_cents / period_months)

    return BurnRateResult(
        period_months=period_months,
        period_start=start,
        period_end=end,
        gross_burn_rate_cents=gross_burn_rate_cents,
        net_burn_rate_cents=net_burn_rate_cents,
        expense_cents=expense_cents,
        revenue_cents=revenue_cents,
        currency=scoped[0].currency if scoped else "USD",
        source_record_ids=_record_ids(scoped),
    )


def compute_runway(
    records: list[FinancialRecord],
    cash_balance_cents: int,
    period_months: int = 3,
    period_end: datetime | None = None,
) -> RunwayResult:
    """Compute runway from current cash and trailing net burn."""
    burn = compute_burn_rate(records, period_months=period_months, period_end=period_end)
    if burn.net_burn_rate_cents <= 0:
        runway_months = None
    else:
        runway_months = round(cash_balance_cents / burn.net_burn_rate_cents, 2)

    return RunwayResult(
        cash_balance_cents=cash_balance_cents,
        monthly_net_burn_cents=burn.net_burn_rate_cents,
        runway_months=runway_months,
        currency=burn.currency,
        burn_rate=burn,
    )


def compute_mrr(
    records: list[FinancialRecord],
    period_months: int = 1,
    period_end: datetime | None = None,
) -> MRRResult:
    """Compute MRR as trailing monthly recurring revenue.

    Stage 1 does not yet have product-plan tables, so this uses normalized
    revenue records and averages over the selected trailing period.
    """
    scoped, start, end = _records_in_period(records, period_months, period_end)
    revenue_records = [
        record
        for record in scoped
        if record.record_type in REVENUE_TYPES and record.amount_cents > 0
    ]
    revenue_cents = sum(record.amount_cents for record in revenue_records)
    mrr_cents = round(revenue_cents / period_months)

    return MRRResult(
        period_months=period_months,
        period_start=start,
        period_end=end,
        mrr_cents=mrr_cents,
        revenue_cents=revenue_cents,
        currency=scoped[0].currency if scoped else "USD",
        source_record_ids=_record_ids(revenue_records),
    )


def compute_arr(mrr: MRRResult) -> ARRResult:
    """Compute ARR from MRR."""
    return ARRResult(
        arr_cents=mrr.mrr_cents * 12,
        mrr_cents=mrr.mrr_cents,
        currency=mrr.currency,
    )


def compute_churn_rate(
    records: list[FinancialRecord],
    period_months: int = 1,
    period_end: datetime | None = None,
) -> ChurnResult:
    """Return a conservative Stage 1 churn placeholder from available data.

    Churn requires customer lifecycle data that is not represented in the
    Stage 1 canonical transaction table. The contract is implemented with
    explicit insufficiency metadata so callers do not mistake it for a real
    computed value.
    """
    _, start, end = _records_in_period(records, period_months, period_end)
    return ChurnResult(
        period_months=period_months,
        period_start=start,
        period_end=end,
        churn_rate=None,
        insufficient_data=True,
        reason="Customer lifecycle data is required to compute churn.",
    )


def compute_cac(records: list[FinancialRecord], new_customers: int) -> CACResult:
    """Compute CAC from sales and marketing spend divided by new customers."""
    marketing_records = [
        record
        for record in records
        if record.category in {"marketing", "sales"} and record.amount_cents < 0
    ]
    spend_cents = sum(abs(record.amount_cents) for record in marketing_records)
    cac_cents = None if new_customers <= 0 else round(spend_cents / new_customers)
    return CACResult(
        new_customers=new_customers,
        sales_marketing_spend_cents=spend_cents,
        cac_cents=cac_cents,
        currency=marketing_records[0].currency if marketing_records else "USD",
        source_record_ids=_record_ids(marketing_records),
    )


def compute_nrr(
    records: list[FinancialRecord],
    period_months: int = 1,
    period_end: datetime | None = None,
) -> NRRResult:
    """Return an explicit Stage 1 NRR placeholder.

    NRR needs opening MRR, expansion, contraction, and churn by account. That
    data arrives later through richer Stripe subscription normalization.
    """
    _, start, end = _records_in_period(records, period_months, period_end)
    return NRRResult(
        period_months=period_months,
        period_start=start,
        period_end=end,
        nrr=None,
        insufficient_data=True,
        reason="Account-level subscription movement is required to compute NRR.",
    )
