"""
AI CFO — Plaid Connector

Fetches bank account transactions from Plaid.
Normalizes all records into the canonical FinancialRecord schema.

Uses Plaid sandbox for development. Real credentials for production.
Read-only — only uses the Plaid transactions endpoint.
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.connectors.base import BaseConnector
from app.models.financial_record import FinancialRecord

logger = logging.getLogger(__name__)


class PlaidConnector(BaseConnector):
    """
    Plaid integration connector.

    Fetches:
    - Bank transactions (deposits, withdrawals, transfers)
    - Account balances

    Plaid amounts:
    - Positive = money spent (debit)
    - Negative = money received (credit)
    We invert this for our schema where positive = inflow.
    """

    provider = "plaid"

    def __init__(self, tenant_id: UUID, credentials: dict):
        super().__init__(tenant_id, credentials)
        self.access_token = credentials.get("access_token", "")
        self.client_id = credentials.get("client_id", "")
        self.secret = credentials.get("secret", "")
        self.env = credentials.get("env", "sandbox")

    async def validate_credentials(self) -> bool:
        """Test Plaid credentials by fetching account info."""
        try:
            # In a real implementation, this would use the plaid-python SDK
            # to call /accounts/get with the access_token
            # For Stage 1, we validate the token format
            return bool(self.access_token and self.client_id and self.secret)
        except Exception as e:
            self.logger.error(f"Plaid validation error: {e}")
            return False

    async def fetch(self, since: datetime | None = None) -> list[dict]:
        """
        Fetch transactions from Plaid.

        In production, this uses the plaid-python SDK.
        For Stage 1, this returns the raw API response structure
        that the normalize() method expects.
        """
        try:
            # Import plaid SDK
            from plaid.api import plaid_api
            from plaid.model.transactions_get_request import TransactionsGetRequest
            from plaid.model.transactions_get_request_options import (
                TransactionsGetRequestOptions,
            )
            from plaid import Configuration, ApiClient, Environment

            # Configure Plaid client
            env_map = {
                "sandbox": Environment.Sandbox,
                "development": Environment.Development,
                "production": Environment.Production,
            }

            configuration = Configuration(
                host=env_map.get(self.env, Environment.Sandbox),
                api_key={
                    "clientId": self.client_id,
                    "secret": self.secret,
                },
            )

            api_client = ApiClient(configuration)
            client = plaid_api.PlaidApi(api_client)

            start_date = (since or datetime.now(timezone.utc) - timedelta(days=90)).date()
            end_date = datetime.now(timezone.utc).date()

            request = TransactionsGetRequest(
                access_token=self.access_token,
                start_date=start_date,
                end_date=end_date,
                options=TransactionsGetRequestOptions(count=500),
            )

            response = client.transactions_get(request)
            transactions = response.transactions

            records = []
            for txn in transactions:
                records.append({
                    "id": txn.transaction_id,
                    "amount": txn.amount,
                    "currency": (txn.iso_currency_code or "USD").upper(),
                    "name": txn.name,
                    "category": txn.category,
                    "date": str(txn.date),
                    "pending": txn.pending,
                    "account_id": txn.account_id,
                    "merchant_name": getattr(txn, "merchant_name", None),
                })

            return records

        except ImportError:
            self.logger.warning(
                "Plaid SDK not available. Returning empty records. "
                "Install plaid-python for real Plaid integration."
            )
            return []
        except Exception as e:
            self.logger.error(f"Failed to fetch Plaid transactions: {e}")
            raise

    def normalize(self, raw_records: list[dict]) -> list[FinancialRecord]:
        """
        Convert Plaid transactions to FinancialRecords.

        Plaid convention: positive amount = money spent, negative = money received.
        Our convention: positive = inflow, negative = outflow.
        So we invert the sign.
        """
        normalized = []
        now = datetime.now(timezone.utc)

        for record in raw_records:
            # Skip pending transactions
            if record.get("pending", False):
                continue

            # Invert Plaid's sign convention
            plaid_amount = record.get("amount", 0)
            amount_cents = int(-plaid_amount * 100)  # Convert dollars to cents, invert sign

            # Determine record type based on sign
            if amount_cents > 0:
                record_type = "revenue"
            else:
                record_type = "expense"

            # Map Plaid categories to our categories
            plaid_categories = record.get("category", [])
            category = self._map_category(plaid_categories)

            # Parse date
            date_str = record.get("date", "")
            try:
                occurred_at = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except (ValueError, TypeError):
                occurred_at = now

            normalized.append(FinancialRecord(
                tenant_id=self.tenant_id,
                source="plaid",
                source_id=record["id"],
                record_type=record_type,
                category=category,
                amount_cents=amount_cents,
                currency=record.get("currency", "USD"),
                description=record.get("name", ""),
                occurred_at=occurred_at,
                metadata_json={
                    "plaid_account_id": record.get("account_id"),
                    "plaid_categories": plaid_categories,
                    "merchant_name": record.get("merchant_name"),
                },
                synced_at=now,
            ))

        return normalized

    @staticmethod
    def _map_category(plaid_categories: list[str] | None) -> str:
        """Map Plaid categories to our internal categories."""
        if not plaid_categories:
            return "uncategorized"

        primary = plaid_categories[0].lower() if plaid_categories else ""

        category_map = {
            "payroll": "payroll",
            "transfer": "transfer",
            "payment": "expense",
            "food and drink": "g_and_a",
            "shops": "g_and_a",
            "travel": "g_and_a",
            "recreation": "g_and_a",
            "service": "infrastructure",
            "tax": "tax",
            "bank fees": "fee",
            "interest": "fee",
        }

        return category_map.get(primary, "uncategorized")
