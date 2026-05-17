"""
AI CFO — Financial Schemas

Pydantic models for financial record API responses.
These are the schemas Person 2 (AI layer) and Person 3 (frontend) build against.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class FinancialRecordResponse(BaseModel):
    """Single normalized financial record."""
    id: uuid.UUID
    source: str
    source_id: str
    record_type: str
    category: str | None
    amount_cents: int
    currency: str
    description: str | None
    occurred_at: datetime
    synced_at: datetime

    model_config = {"from_attributes": True}


class TenantResponse(BaseModel):
    """Tenant information response."""
    id: uuid.UUID
    name: str
    slug: str
    jurisdiction: str
    autopilot_level: str
    shadow_mode_until: datetime
    is_in_shadow_mode: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BurnRateResult(BaseModel):
    """Deterministic burn-rate result with source record traceability."""

    period_months: int
    period_start: datetime
    period_end: datetime
    gross_burn_rate_cents: int
    net_burn_rate_cents: int
    expense_cents: int
    revenue_cents: int
    currency: str
    source_record_ids: list[uuid.UUID]


class RunwayResult(BaseModel):
    """Runway result derived from cash balance and net burn."""

    cash_balance_cents: int
    monthly_net_burn_cents: int
    runway_months: float | None
    currency: str
    burn_rate: BurnRateResult


class MRRResult(BaseModel):
    """Monthly recurring revenue approximation for Stage 1."""

    period_months: int
    period_start: datetime
    period_end: datetime
    mrr_cents: int
    revenue_cents: int
    currency: str
    source_record_ids: list[uuid.UUID]


class ARRResult(BaseModel):
    """Annual recurring revenue derived from MRR."""

    arr_cents: int
    mrr_cents: int
    currency: str


class ChurnResult(BaseModel):
    """Churn contract. May explicitly report insufficient data."""

    period_months: int
    period_start: datetime
    period_end: datetime
    churn_rate: float | None
    insufficient_data: bool
    reason: str | None = None


class CACResult(BaseModel):
    """Customer acquisition cost result."""

    new_customers: int
    sales_marketing_spend_cents: int
    cac_cents: int | None
    currency: str
    source_record_ids: list[uuid.UUID]


class NRRResult(BaseModel):
    """Net revenue retention contract. May explicitly report insufficient data."""

    period_months: int
    period_start: datetime
    period_end: datetime
    nrr: float | None
    insufficient_data: bool
    reason: str | None = None


class FinancialSnapshotResponse(BaseModel):
    """Stage 1 dashboard and AI financial snapshot contract."""

    burn_rate: BurnRateResult
    runway: RunwayResult | None
    mrr: MRRResult
    arr: ARRResult
    record_count: int
