"""
AI CFO — Connector Tests

Tests for integration connector endpoints and normalization logic.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestConnectorEndpoints:
    """Tests for integration connector API endpoints."""

    async def test_connect_stripe(self, client: AsyncClient, auth_headers: dict):
        """Connecting Stripe stores config and returns status."""
        response = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_fake_key"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "stripe"
        assert data["status"] == "active"
        assert data["permissions"] == "read_only"

    async def test_connect_plaid(self, client: AsyncClient, auth_headers: dict):
        """Connecting Plaid stores config and returns status."""
        response = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "plaid",
                "credentials": {
                    "access_token": "access-sandbox-test",
                    "client_id": "test_client_id",
                    "secret": "test_secret",
                },
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "plaid"
        assert data["status"] == "active"

    async def test_connect_invalid_provider(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Connecting an unsupported provider is rejected."""
        response = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "invalid_provider",
                "credentials": {"key": "value"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 422  # Pydantic validation

    async def test_status_after_connect(
        self, client: AsyncClient, auth_headers: dict
    ):
        """After connecting, the integration appears in status list."""
        # Connect Stripe
        await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_fake_key"},
            },
            headers=auth_headers,
        )

        # Check status
        response = await client.get(
            "/api/v1/integrations/status", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["connectors"]) == 1
        assert data["connectors"][0]["provider"] == "stripe"

    async def test_reconnect_updates_existing(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Reconnecting the same provider updates the existing config."""
        # First connect
        await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_old_key"},
            },
            headers=auth_headers,
        )

        # Reconnect with new key
        response = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_new_key"},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

        # Should still be one connector
        status_response = await client.get(
            "/api/v1/integrations/status", headers=auth_headers
        )
        assert len(status_response.json()["connectors"]) == 1


@pytest.mark.asyncio
class TestStripeNormalization:
    """Tests for Stripe data normalization logic."""

    def test_normalize_charge_to_revenue(self):
        """A successful Stripe charge normalizes to a revenue record."""
        from uuid import uuid4
        from app.connectors.stripe_connector import StripeConnector

        connector = StripeConnector(
            tenant_id=uuid4(),
            credentials={"api_key": "test"},
        )

        raw_records = [
            {
                "type": "charge",
                "id": "ch_test_123",
                "amount": 5000,  # $50.00
                "currency": "USD",
                "description": "Subscription payment",
                "created": 1700000000,
                "status": "succeeded",
                "refunded": False,
                "metadata": {},
                "customer": "cus_test",
            }
        ]

        normalized = connector.normalize(raw_records)
        assert len(normalized) == 1
        record = normalized[0]
        assert record.source == "stripe"
        assert record.source_id == "ch_test_123"
        assert record.record_type == "revenue"
        assert record.amount_cents == 5000
        assert record.currency == "USD"

    def test_failed_charge_skipped(self):
        """Failed Stripe charges are not normalized."""
        from uuid import uuid4
        from app.connectors.stripe_connector import StripeConnector

        connector = StripeConnector(
            tenant_id=uuid4(),
            credentials={"api_key": "test"},
        )

        raw_records = [
            {
                "type": "charge",
                "id": "ch_failed",
                "amount": 5000,
                "currency": "USD",
                "description": "Failed payment",
                "created": 1700000000,
                "status": "failed",
                "refunded": False,
                "metadata": {},
                "customer": "cus_test",
            }
        ]

        normalized = connector.normalize(raw_records)
        assert len(normalized) == 0

    def test_refund_has_negative_amount(self):
        """Stripe refunds normalize to negative amounts."""
        from uuid import uuid4
        from app.connectors.stripe_connector import StripeConnector

        connector = StripeConnector(
            tenant_id=uuid4(),
            credentials={"api_key": "test"},
        )

        raw_records = [
            {
                "type": "refund",
                "id": "re_test_123",
                "amount": 2500,
                "currency": "USD",
                "description": "Refund",
                "created": 1700000000,
                "status": "succeeded",
                "metadata": {},
                "charge_id": "ch_test_123",
            }
        ]

        normalized = connector.normalize(raw_records)
        assert len(normalized) == 1
        assert normalized[0].amount_cents == -2500
        assert normalized[0].record_type == "refund"


@pytest.mark.asyncio
class TestPlaidNormalization:
    """Tests for Plaid data normalization logic."""

    def test_plaid_sign_inversion(self):
        """Plaid amounts are inverted: positive (debit) → negative (outflow)."""
        from uuid import uuid4
        from app.connectors.plaid_connector import PlaidConnector

        connector = PlaidConnector(
            tenant_id=uuid4(),
            credentials={
                "access_token": "test",
                "client_id": "test",
                "secret": "test",
            },
        )

        raw_records = [
            {
                "id": "txn_001",
                "amount": 25.50,  # Plaid: positive = money spent
                "currency": "USD",
                "name": "AWS Monthly",
                "category": ["Service"],
                "date": "2024-01-15",
                "pending": False,
                "account_id": "acc_test",
                "merchant_name": "Amazon Web Services",
            }
        ]

        normalized = connector.normalize(raw_records)
        assert len(normalized) == 1
        record = normalized[0]
        assert record.amount_cents == -2550  # Inverted and in cents
        assert record.record_type == "expense"

    def test_pending_transactions_skipped(self):
        """Pending Plaid transactions are not normalized."""
        from uuid import uuid4
        from app.connectors.plaid_connector import PlaidConnector

        connector = PlaidConnector(
            tenant_id=uuid4(),
            credentials={
                "access_token": "test",
                "client_id": "test",
                "secret": "test",
            },
        )

        raw_records = [
            {
                "id": "txn_pending",
                "amount": 100.00,
                "currency": "USD",
                "name": "Pending charge",
                "category": [],
                "date": "2024-01-15",
                "pending": True,
                "account_id": "acc_test",
                "merchant_name": None,
            }
        ]

        normalized = connector.normalize(raw_records)
        assert len(normalized) == 0
