"""Stage 1 end-to-end validation using test-only mocked Stripe data."""

import asyncio
from datetime import datetime, timezone
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.connectors.stripe_connector import StripeConnector
from app.models.audit_log import AuditLog
from app.models.connector_config import ConnectorConfig
from app.models.financial_record import FinancialRecord
from app.services.sync_service import sync_connector_records
from tests.conftest import TEST_DATABASE_URL


SYNC_TEST_DATABASE_URL = TEST_DATABASE_URL.replace("+asyncpg", "")


def _stripe_records(amount: int = 120000) -> list[dict]:
    created = int(datetime(2026, 5, 1, tzinfo=timezone.utc).timestamp())
    return [
        {
            "type": "charge",
            "id": "ch_mock_success",
            "amount": amount,
            "currency": "USD",
            "description": "Mock subscription payment",
            "created": created,
            "status": "succeeded",
            "refunded": False,
            "metadata": {"plan": "growth"},
            "customer": "cus_mock",
        },
        {
            "type": "charge",
            "id": "ch_mock_failed",
            "amount": 50000,
            "currency": "USD",
            "description": "Failed mock payment",
            "created": created,
            "status": "failed",
            "refunded": False,
            "metadata": {},
            "customer": "cus_failed",
        },
        {
            "type": "refund",
            "id": "re_mock_refund",
            "amount": 20000,
            "currency": "USD",
            "description": "Mock refund",
            "created": created,
            "status": "succeeded",
            "metadata": {},
            "charge_id": "ch_mock_success",
        },
        {
            "type": "charge",
            "id": "ch_mock_success",
            "amount": amount,
            "currency": "USD",
            "description": "Duplicate in same sync should be skipped",
            "created": created,
            "status": "succeeded",
            "refunded": False,
            "metadata": {},
            "customer": "cus_mock",
        },
    ]


@pytest.mark.asyncio
async def test_stage1_mock_stripe_sync_to_financial_metrics(
    client: AsyncClient,
    db_session,
    monkeypatch,
):
    async def fake_fetch(self, since=None):
        return _stripe_records()

    monkeypatch.setattr(StripeConnector, "fetch", fake_fetch)

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "mock-stripe@startup.com",
            "password": "SecurePass123!",
            "full_name": "Mock Founder",
            "company_name": "Mock Stripe Startup",
            "jurisdiction": "IN",
        },
    )
    assert register_response.status_code == 201
    auth = register_response.json()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}

    connect_response = await client.post(
        "/api/v1/integrations/connect",
        json={"provider": "stripe", "credentials": {"api_key": "sk_test_mock_only"}},
        headers=headers,
    )
    assert connect_response.status_code == 201
    connector_id = connect_response.json()["id"]
    tenant_id = UUID(auth["user"]["tenant_id"])
    connector_uuid = UUID(connector_id)
    await db_session.commit()

    def run_sync_and_assert():
        engine = create_engine(SYNC_TEST_DATABASE_URL, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        with Session() as sync_session:
            result = sync_connector_records(
                session=sync_session,
                tenant_id=tenant_id,
                connector_id=connector_uuid,
                provider="stripe",
                connector_class=StripeConnector,
            )
            assert result == {
                "status": "success",
                "provider": "stripe",
                "inserted": 2,
                "updated": 0,
                "skipped": 1,
            }

            records = (
                sync_session.query(FinancialRecord)
                .filter(FinancialRecord.tenant_id == tenant_id)
                .order_by(FinancialRecord.source_id)
                .all()
            )
            assert [record.source_id for record in records] == [
                "ch_mock_success",
                "re_mock_refund",
            ]
            assert sum(record.amount_cents for record in records) == 100000

            config = sync_session.query(ConnectorConfig).filter_by(id=connector_uuid).one()
            assert config.status == "active"
            assert config.last_synced_at is not None
            assert config.sync_error is None

            audit = (
                sync_session.query(AuditLog)
                .filter(
                    AuditLog.tenant_id == tenant_id,
                    AuditLog.action_type == "connector.sync",
                )
                .one()
            )
            assert audit.outcome == "success"
            assert audit.action_detail["inserted"] == 2

    await asyncio.to_thread(run_sync_and_assert)

    burn_response = await client.get(
        "/api/v1/financials/burn?period_months=1",
        headers=headers,
    )
    assert burn_response.status_code == 200
    burn = burn_response.json()
    assert burn["revenue_cents"] == 120000
    assert burn["net_burn_rate_cents"] == 0


@pytest.mark.asyncio
async def test_stage1_mock_stripe_second_sync_updates_existing(
    client: AsyncClient,
    db_session,
    monkeypatch,
):
    async def first_fetch(self, since=None):
        return _stripe_records(amount=120000)

    async def second_fetch(self, since=None):
        return _stripe_records(amount=150000)

    monkeypatch.setattr(StripeConnector, "fetch", first_fetch)

    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "mock-stripe-update@startup.com",
            "password": "SecurePass123!",
            "full_name": "Mock Founder",
            "company_name": "Mock Stripe Update Startup",
        },
    )
    auth = register_response.json()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    connect_response = await client.post(
        "/api/v1/integrations/connect",
        json={"provider": "stripe", "credentials": {"api_key": "sk_test_mock_only"}},
        headers=headers,
    )
    await db_session.commit()

    tenant_id = UUID(auth["user"]["tenant_id"])
    connector_id = UUID(connect_response.json()["id"])
    def run_first_sync():
        engine = create_engine(SYNC_TEST_DATABASE_URL, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        with Session() as sync_session:
            first = sync_connector_records(
                session=sync_session,
                tenant_id=tenant_id,
                connector_id=connector_id,
                provider="stripe",
                connector_class=StripeConnector,
            )
            assert first["inserted"] == 2

    await asyncio.to_thread(run_first_sync)

    monkeypatch.setattr(StripeConnector, "fetch", second_fetch)

    def run_second_sync_and_assert():
        engine = create_engine(SYNC_TEST_DATABASE_URL, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        with Session() as sync_session:
            second = sync_connector_records(
                session=sync_session,
                tenant_id=tenant_id,
                connector_id=connector_id,
                provider="stripe",
                connector_class=StripeConnector,
            )
            assert second["inserted"] == 0
            assert second["updated"] == 2

            charge = (
                sync_session.query(FinancialRecord)
                .filter(
                    FinancialRecord.tenant_id == tenant_id,
                    FinancialRecord.source_id == "ch_mock_success",
                )
                .one()
            )
            assert charge.amount_cents == 150000

    await asyncio.to_thread(run_second_sync_and_assert)
