"""Tests for deterministic financial calculations and endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient

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
from app.models.tenant import Tenant


def _record(
    *,
    tenant_id,
    source_id: str,
    record_type: str,
    amount_cents: int,
    days_ago: int = 10,
    category: str | None = None,
) -> FinancialRecord:
    now = datetime.now(timezone.utc)
    return FinancialRecord(
        tenant_id=tenant_id,
        source="manual",
        source_id=source_id,
        record_type=record_type,
        category=category,
        amount_cents=amount_cents,
        currency="USD",
        description=source_id,
        occurred_at=now - timedelta(days=days_ago),
        synced_at=now,
    )


class TestFinancialCalculations:
    def test_compute_burn_rate_uses_trailing_period(self):
        tenant_id = uuid4()
        records = [
            _record(
                tenant_id=tenant_id,
                source_id="aws",
                record_type="expense",
                amount_cents=-90000,
            ),
            _record(
                tenant_id=tenant_id,
                source_id="revenue",
                record_type="revenue",
                amount_cents=30000,
            ),
            _record(
                tenant_id=tenant_id,
                source_id="old",
                record_type="expense",
                amount_cents=-999999,
                days_ago=200,
            ),
        ]

        result = compute_burn_rate(records, period_months=3)

        assert result.expense_cents == 90000
        assert result.revenue_cents == 30000
        assert result.gross_burn_rate_cents == 30000
        assert result.net_burn_rate_cents == 20000

    def test_compute_runway_returns_none_when_cash_flow_positive(self):
        tenant_id = uuid4()
        records = [
            _record(
                tenant_id=tenant_id,
                source_id="revenue",
                record_type="revenue",
                amount_cents=90000,
            ),
            _record(
                tenant_id=tenant_id,
                source_id="expense",
                record_type="expense",
                amount_cents=-30000,
            ),
        ]

        result = compute_runway(records, cash_balance_cents=100000, period_months=1)

        assert result.monthly_net_burn_cents == 0
        assert result.runway_months is None

    def test_mrr_arr_and_cac_contracts(self):
        tenant_id = uuid4()
        records = [
            _record(
                tenant_id=tenant_id,
                source_id="revenue",
                record_type="revenue",
                amount_cents=120000,
            ),
            _record(
                tenant_id=tenant_id,
                source_id="marketing",
                record_type="expense",
                amount_cents=-50000,
                category="marketing",
            ),
        ]

        mrr = compute_mrr(records, period_months=1)
        arr = compute_arr(mrr)
        cac = compute_cac(records, new_customers=5)

        assert mrr.mrr_cents == 120000
        assert arr.arr_cents == 1440000
        assert cac.cac_cents == 10000

    def test_churn_and_nrr_report_insufficient_data(self):
        tenant_id = uuid4()
        records = [
            _record(
                tenant_id=tenant_id,
                source_id="revenue",
                record_type="revenue",
                amount_cents=120000,
            )
        ]

        churn = compute_churn_rate(records)
        nrr = compute_nrr(records)

        assert churn.insufficient_data is True
        assert churn.churn_rate is None
        assert nrr.insufficient_data is True
        assert nrr.nrr is None


@pytest.mark.asyncio
class TestFinancialEndpoints:
    async def test_burn_endpoint_is_tenant_scoped(
        self,
        client: AsyncClient,
        db_session,
        test_tenant,
        auth_headers: dict,
    ):
        other_tenant = Tenant(
            name="Other Startup",
            slug=f"other-{uuid4().hex[:8]}",
            jurisdiction="US",
        )
        db_session.add(other_tenant)
        await db_session.flush()

        db_session.add_all(
            [
                _record(
                    tenant_id=test_tenant.id,
                    source_id="tenant-expense",
                    record_type="expense",
                    amount_cents=-120000,
                ),
                _record(
                    tenant_id=other_tenant.id,
                    source_id="other-tenant-expense",
                    record_type="expense",
                    amount_cents=-999999,
                ),
            ]
        )
        await db_session.flush()

        response = await client.get(
            "/api/v1/financials/burn?period_months=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expense_cents"] == 120000
        assert data["gross_burn_rate_cents"] == 40000

    async def test_metric_endpoints_return_stage2_contracts(
        self,
        client: AsyncClient,
        db_session,
        test_tenant,
        auth_headers: dict,
    ):
        db_session.add_all(
            [
                _record(
                    tenant_id=test_tenant.id,
                    source_id="revenue",
                    record_type="revenue",
                    amount_cents=120000,
                ),
                _record(
                    tenant_id=test_tenant.id,
                    source_id="marketing",
                    record_type="expense",
                    amount_cents=-50000,
                    category="marketing",
                ),
            ]
        )
        await db_session.flush()

        mrr = await client.get("/api/v1/financials/mrr", headers=auth_headers)
        arr = await client.get("/api/v1/financials/arr", headers=auth_headers)
        cac = await client.get(
            "/api/v1/financials/cac?new_customers=5",
            headers=auth_headers,
        )
        churn = await client.get("/api/v1/financials/churn", headers=auth_headers)
        nrr = await client.get("/api/v1/financials/nrr", headers=auth_headers)

        assert mrr.status_code == 200
        assert mrr.json()["mrr_cents"] == 120000
        assert arr.status_code == 200
        assert arr.json()["arr_cents"] == 1440000
        assert cac.status_code == 200
        assert cac.json()["cac_cents"] == 10000
        assert churn.status_code == 200
        assert churn.json()["insufficient_data"] is True
        assert nrr.status_code == 200
        assert nrr.json()["insufficient_data"] is True
