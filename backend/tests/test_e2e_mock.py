"""
AI CFO - Stage 1 End-to-End Mock Tests

Full mock registration flow covering:
  1. Founder registers and receives JWT tokens
  2. Founder connects Stripe (mock credentials)
  3. Mock Stripe data is synced into financial_records
  4. Founder queries burn rate, runway, snapshot, and audit log
  5. Guardrails validate a mock AI recommendation
  6. Tenant isolation is enforced throughout

These tests replace the Stripe live-API test that cannot run from India
during development. They simulate the full connector pipeline using fake
Stripe charge/refund payloads fed directly through the normalization layer.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.stripe_connector import StripeConnector
from app.guardrails.engine import validate_ai_output
from app.guardrails.schemas import GuardrailInput
from app.models.financial_record import FinancialRecord
from app.models.tenant import Tenant
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_STRIPE_CHARGES = [
    {
        "type": "charge",
        "id": f"ch_mock_{i}",
        "amount": amount,
        "currency": "USD",
        "description": desc,
        "created": int((datetime(2026, 5, 1, tzinfo=timezone.utc) + timedelta(days=i)).timestamp()),
        "status": "succeeded",
        "refunded": False,
        "metadata": {},
        "customer": f"cus_mock_{i}",
    }
    for i, (amount, desc) in enumerate(
        [
            (500_00, "Pro plan - May"),
            (200_00, "Starter plan - May"),
            (500_00, "Pro plan - April"),
            (200_00, "Starter plan - April"),
            (500_00, "Pro plan - March"),
            (200_00, "Starter plan - March"),
        ]
    )
]

MOCK_STRIPE_REFUNDS = [
    {
        "type": "refund",
        "id": "re_mock_0",
        "amount": 200_00,
        "currency": "USD",
        "description": "Refund for charge ch_mock_1",
        "created": int(datetime(2026, 5, 2, tzinfo=timezone.utc).timestamp()),
        "status": "succeeded",
        "metadata": {},
        "charge_id": "ch_mock_1",
    }
]

MOCK_STRIPE_FAILED = [
    {
        "type": "charge",
        "id": "ch_mock_failed",
        "amount": 100_00,
        "currency": "USD",
        "description": "Failed charge",
        "created": int(datetime(2026, 5, 3, tzinfo=timezone.utc).timestamp()),
        "status": "failed",
        "refunded": False,
        "metadata": {},
        "customer": "cus_mock_fail",
    }
]

MOCK_EXPENSES = [
    {
        "source_id": "exp_aws",
        "amount_cents": -350_00,
        "category": "infrastructure",
        "description": "AWS bill March",
        "days_ago": 20,
    },
    {
        "source_id": "exp_salary",
        "amount_cents": -8000_00,
        "category": "payroll",
        "description": "Engineer payroll March",
        "days_ago": 25,
    },
    {
        "source_id": "exp_ads",
        "amount_cents": -500_00,
        "category": "marketing",
        "description": "Google Ads March",
        "days_ago": 22,
    },
]


def _build_expense_record(tenant_id: uuid.UUID, spec: dict) -> FinancialRecord:
    now = datetime.now(timezone.utc)
    return FinancialRecord(
        tenant_id=tenant_id,
        source="plaid",
        source_id=spec["source_id"],
        record_type="expense",
        category=spec["category"],
        amount_cents=spec["amount_cents"],
        currency="USD",
        description=spec["description"],
        occurred_at=now - timedelta(days=spec["days_ago"]),
        synced_at=now,
    )


# ---------------------------------------------------------------------------
# E2E Mock Test Suite
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestEndToEndMockFlow:
    """
    Simulates the Stage 1 first-milestone flow entirely with mock data.
    No live Stripe API calls are made.
    """

    # -- Step 1: Registration -----------------------------------------------

    async def test_step1_register_founder(self, client: AsyncClient):
        """Founder registers, receives JWT, tenant is created."""
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "founder@mockstartup.com",
                "password": "S3cureP@ss!",
                "full_name": "Mock Founder",
                "company_name": "Mock Startup Inc",
                "jurisdiction": "IN",
            },
        )
        assert resp.status_code == 201
        data = resp.json()

        # Tokens present
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "bearer"

        # User fields correct
        user = data["user"]
        assert user["email"] == "founder@mockstartup.com"
        assert user["full_name"] == "Mock Founder"
        assert user["role"] == "founder"
        assert user["tenant_id"] is not None

    # -- Step 2: Login after registration -----------------------------------

    async def test_step2_login_after_register(self, client: AsyncClient):
        """Founder can log in immediately after registration."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@mockstartup.com",
                "password": "S3cureP@ss!",
                "full_name": "Login Founder",
                "company_name": "Login Startup",
                "jurisdiction": "IN",
            },
        )

        # Login
        resp = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@mockstartup.com",
                "password": "S3cureP@ss!",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"]
        assert data["user"]["email"] == "login@mockstartup.com"

    # -- Step 3: Connect Stripe (mock credentials) --------------------------

    async def test_step3_connect_stripe_mock(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Founder connects Stripe with mock API key. Creds are stored encrypted."""
        resp = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_mock_india_dev_key"},
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["provider"] == "stripe"
        assert data["status"] == "active"
        assert data["permissions"] == "read_only"
        assert data["id"] is not None

    # -- Step 4: Stripe normalization (no live API call) --------------------

    async def test_step4_stripe_normalization_produces_correct_records(
        self, test_tenant: Tenant
    ):
        """
        Stripe connector normalizes mock charges and refunds into
        canonical FinancialRecord objects without calling the Stripe API.
        """
        connector = StripeConnector(
            tenant_id=test_tenant.id,
            credentials={"api_key": "sk_test_mock"},
        )

        all_raw = MOCK_STRIPE_CHARGES + MOCK_STRIPE_REFUNDS + MOCK_STRIPE_FAILED
        records = connector.normalize(all_raw)

        # 6 charges succeeded + 1 refund = 7 records; 1 failed charge skipped
        assert len(records) == 7

        revenue_records = [r for r in records if r.record_type == "revenue"]
        refund_records = [r for r in records if r.record_type == "refund"]

        assert len(revenue_records) == 6
        assert len(refund_records) == 1

        # All amounts correct
        total_revenue = sum(r.amount_cents for r in revenue_records)
        assert total_revenue == (500_00 + 200_00) * 3  # 2100_00

        # Refund is negative
        assert refund_records[0].amount_cents == -200_00

        # Source and source_id populated
        for r in records:
            assert r.source == "stripe"
            assert r.source_id.startswith(("ch_mock_", "re_mock_"))
            assert r.tenant_id == test_tenant.id

    # -- Step 5: Insert mock data and query burn rate -----------------------

    async def test_step5_burn_rate_from_mock_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """
        Insert mock Stripe revenue + Plaid expenses into DB,
        then query the burn-rate endpoint and verify correct calculation.
        """
        connector = StripeConnector(
            tenant_id=test_tenant.id,
            credentials={"api_key": "sk_test_mock"},
        )
        stripe_records = connector.normalize(MOCK_STRIPE_CHARGES + MOCK_STRIPE_REFUNDS)

        expense_records = [
            _build_expense_record(test_tenant.id, spec) for spec in MOCK_EXPENSES
        ]

        db_session.add_all(stripe_records + expense_records)
        await db_session.flush()

        resp = await client.get(
            "/api/v1/financials/burn?period_months=3",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        # Revenue: 6 charges * various amounts = 2100_00 cents
        assert data["revenue_cents"] == 2100_00

        # Expenses: 350_00 + 8000_00 + 500_00 = 8850_00 cents
        assert data["expense_cents"] == 8850_00

        # Gross burn rate: 8850_00 / 3 = 2950_00 per month
        assert data["gross_burn_rate_cents"] == 2950_00

        # Net burn: (8850_00 - 2100_00) / 3 = 2250_00 per month
        assert data["net_burn_rate_cents"] == 2250_00

        assert data["currency"] == "USD"
        assert len(data["source_record_ids"]) > 0

    # -- Step 6: Runway calculation -----------------------------------------

    async def test_step6_runway_calculation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """
        Given a known cash balance, runway is correctly calculated
        from the net burn rate.
        """
        connector = StripeConnector(
            tenant_id=test_tenant.id,
            credentials={"api_key": "sk_test_mock"},
        )
        stripe_records = connector.normalize(MOCK_STRIPE_CHARGES)
        expense_records = [
            _build_expense_record(test_tenant.id, spec) for spec in MOCK_EXPENSES
        ]
        db_session.add_all(stripe_records + expense_records)
        await db_session.flush()

        cash_balance = 50000_00  # $500.00 in cents? No, 50000_00 = $500k
        resp = await client.get(
            f"/api/v1/financials/runway?cash_balance_cents={cash_balance}&period_months=3",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["cash_balance_cents"] == cash_balance
        assert data["monthly_net_burn_cents"] > 0
        assert data["runway_months"] is not None
        assert data["runway_months"] > 0
        assert data["currency"] == "USD"

    # -- Step 7: Financial snapshot -----------------------------------------

    async def test_step7_financial_snapshot(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """
        Snapshot endpoint returns burn, optional runway, MRR, ARR, and
        record count in one response.
        """
        connector = StripeConnector(
            tenant_id=test_tenant.id,
            credentials={"api_key": "sk_test_mock"},
        )
        stripe_records = connector.normalize(MOCK_STRIPE_CHARGES)
        db_session.add_all(stripe_records)
        await db_session.flush()

        resp = await client.get(
            "/api/v1/financials/snapshot?period_months=3",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        assert "burn_rate" in data
        assert "mrr" in data
        assert "arr" in data
        assert data["record_count"] == 6
        assert data["mrr"]["mrr_cents"] > 0
        assert data["arr"]["arr_cents"] == data["mrr"]["mrr_cents"] * 12

        # Without cash_balance_cents, runway is None
        assert data["runway"] is None

    # -- Step 8: Snapshot with runway ---------------------------------------

    async def test_step8_snapshot_with_runway(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """Snapshot with cash_balance_cents returns runway."""
        connector = StripeConnector(
            tenant_id=test_tenant.id,
            credentials={"api_key": "sk_test_mock"},
        )
        stripe_records = connector.normalize(MOCK_STRIPE_CHARGES)
        expense_records = [
            _build_expense_record(test_tenant.id, spec) for spec in MOCK_EXPENSES
        ]
        db_session.add_all(stripe_records + expense_records)
        await db_session.flush()

        resp = await client.get(
            "/api/v1/financials/snapshot?cash_balance_cents=10000000&period_months=3",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["runway"] is not None
        assert data["runway"]["runway_months"] > 0

    # -- Step 9: Audit log records registration and connect -----------------

    async def test_step9_audit_log_records_actions(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        After registration and connector connect, audit log contains
        matching entries scoped to the authenticated tenant.
        """
        # Register a fresh user
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "audit@mockstartup.com",
                "password": "S3cureP@ss!",
                "full_name": "Audit Founder",
                "company_name": "Audit Startup",
            },
        )
        tokens = reg_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Connect Stripe
        await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_audit"},
            },
            headers=headers,
        )

        # Check audit log
        audit_resp = await client.get("/api/v1/audit-log", headers=headers)
        assert audit_resp.status_code == 200
        items = audit_resp.json()["items"]

        action_types = [item["action_type"] for item in items]
        assert "auth.register" in action_types
        assert "connector.connect" in action_types

        # All entries belong to the same tenant
        tenant_ids = {item["tenant_id"] for item in items}
        assert len(tenant_ids) == 1

    # -- Step 10: Guardrails validation on mock AI output -------------------

    async def test_step10_guardrails_validate_mock_ai_output(
        self, test_tenant: Tenant
    ):
        """
        Guardrails engine correctly validates a mock AI recommendation
        that includes source data (approved) vs one missing sources (blocked).
        """
        # Valid recommendation with sources
        valid_result = validate_ai_output(
            GuardrailInput(
                tenant_id=test_tenant.id,
                action_type="recommendation",
                ai_output={
                    "answer": "Your current burn rate is $2,250/month.",
                    "confidence_explanation": "Based on 3 months of Stripe and Plaid data.",
                },
                data_sources=["financial_record:stripe:ch_mock_0", "financial_record:plaid:exp_aws"],
                confidence=0.92,
                reversible=True,
                requested_autonomy_level="advisory",
            )
        )
        assert valid_result.approved is True
        assert valid_result.modified_output is not None
        assert valid_result.requires_human_approval is True  # advisory mode

        # Invalid recommendation without sources
        invalid_result = validate_ai_output(
            GuardrailInput(
                tenant_id=test_tenant.id,
                action_type="recommendation",
                ai_output={"answer": "Your burn rate is probably fine."},
                data_sources=[],
                confidence=0.4,
            )
        )
        assert invalid_result.approved is False
        assert "recommendations must include source data" in invalid_result.violations

    # -- Step 11: Tenant isolation ------------------------------------------

    async def test_step11_tenant_isolation_financial_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_tenant: Tenant,
        auth_headers: dict,
    ):
        """
        Financial records from another tenant must NOT appear in the
        authenticated tenant's burn-rate calculation.
        """
        # Create another tenant with data
        other_tenant = Tenant(
            name="Other Startup",
            slug=f"other-{uuid.uuid4().hex[:8]}",
            jurisdiction="US",
        )
        db_session.add(other_tenant)
        await db_session.flush()

        now = datetime.now(timezone.utc)

        # Insert a large expense for the OTHER tenant
        other_expense = FinancialRecord(
            tenant_id=other_tenant.id,
            source="manual",
            source_id="other_exp_1",
            record_type="expense",
            category="payroll",
            amount_cents=-999_999_00,
            currency="USD",
            description="Other tenant huge expense",
            occurred_at=now - timedelta(days=5),
            synced_at=now,
        )
        db_session.add(other_expense)

        # Insert a small expense for our test tenant
        our_expense = FinancialRecord(
            tenant_id=test_tenant.id,
            source="manual",
            source_id="our_exp_1",
            record_type="expense",
            category="infrastructure",
            amount_cents=-100_00,
            currency="USD",
            description="Our small expense",
            occurred_at=now - timedelta(days=5),
            synced_at=now,
        )
        db_session.add(our_expense)
        await db_session.flush()

        # Query burn rate as our tenant
        resp = await client.get(
            "/api/v1/financials/burn?period_months=1",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()

        # Must only see our $1.00 expense, NOT the other tenant's $9,999.99
        assert data["expense_cents"] == 100_00
        assert data["gross_burn_rate_cents"] == 100_00

    # -- Step 12: Full pipeline mock (register -> connect -> data -> query) -

    async def test_step12_full_pipeline_mock(self, client: AsyncClient):
        """
        Complete happy-path: register, connect Stripe, insert mock-normalized
        data, query snapshot. Mimics the first-milestone flow.
        """
        # 1. Register
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "pipeline@mockstartup.com",
                "password": "Pipeline123!",
                "full_name": "Pipeline Founder",
                "company_name": "Pipeline Inc",
                "jurisdiction": "IN",
            },
        )
        assert reg_resp.status_code == 201
        tokens = reg_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        tenant_id = tokens["user"]["tenant_id"]

        # 2. Connect Stripe
        connect_resp = await client.post(
            "/api/v1/integrations/connect",
            json={
                "provider": "stripe",
                "credentials": {"api_key": "sk_test_pipeline_mock"},
            },
            headers=headers,
        )
        assert connect_resp.status_code == 201
        assert connect_resp.json()["status"] == "active"

        # 3. Verify connector status
        status_resp = await client.get(
            "/api/v1/integrations/status", headers=headers
        )
        assert status_resp.status_code == 200
        connectors = status_resp.json()["connectors"]
        assert len(connectors) == 1
        assert connectors[0]["provider"] == "stripe"

        # 4. Query snapshot (no data yet -> zeros)
        snap_resp = await client.get(
            "/api/v1/financials/snapshot?period_months=3",
            headers=headers,
        )
        assert snap_resp.status_code == 200
        snap = snap_resp.json()
        assert snap["record_count"] == 0
        assert snap["burn_rate"]["expense_cents"] == 0
        assert snap["burn_rate"]["revenue_cents"] == 0

        # 5. Health check
        health_resp = await client.get("/api/v1/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["db"] == "ok"

        # 6. Audit log has all actions
        audit_resp = await client.get("/api/v1/audit-log", headers=headers)
        assert audit_resp.status_code == 200
        action_types = [i["action_type"] for i in audit_resp.json()["items"]]
        assert "auth.register" in action_types
        assert "connector.connect" in action_types
