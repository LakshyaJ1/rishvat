"""
AI CFO — Stripe Connector

Fetches revenue, subscription, refund, and fee data from Stripe.
Normalizes all records into the canonical FinancialRecord schema.

Read-only by default — only uses the Stripe read API.
Write operations (price changes, etc.) require separate write credentials.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

import stripe

from app.connectors.base import BaseConnector
from app.models.financial_record import FinancialRecord

logger = logging.getLogger(__name__)


class StripeConnector(BaseConnector):
    """
    Stripe integration connector.

    Fetches:
    - Charges (revenue)
    - Refunds
    - Subscription invoices
    - Application fees

    All amounts are already in cents from Stripe (perfect for our schema).
    """

    provider = "stripe"

    def __init__(self, tenant_id: UUID, credentials: dict):
        super().__init__(tenant_id, credentials)
        self.api_key = credentials.get("api_key", "")

    async def validate_credentials(self) -> bool:
        """Test Stripe credentials by fetching account info."""
        try:
            stripe.api_key = self.api_key
            stripe.Account.retrieve()
            return True
        except stripe.error.AuthenticationError:
            return False
        except Exception as e:
            self.logger.error(f"Stripe validation error: {e}")
            return False

    async def fetch(self, since: datetime | None = None) -> list[dict]:
        """
        Fetch charges and refunds from Stripe.
        Uses auto-pagination to get all records.
        """
        stripe.api_key = self.api_key
        records = []

        # Fetch charges (revenue)
        params = {"limit": 100}
        if since:
            params["created"] = {"gte": int(since.timestamp())}

        try:
            charges = stripe.Charge.list(**params)
            for charge in charges.auto_paging_iter():
                records.append({
                    "type": "charge",
                    "id": charge.id,
                    "amount": charge.amount,
                    "currency": charge.currency.upper(),
                    "description": charge.description or f"Stripe charge {charge.id}",
                    "created": charge.created,
                    "status": charge.status,
                    "refunded": charge.refunded,
                    "metadata": dict(charge.metadata) if charge.metadata else {},
                    "customer": charge.customer,
                })
        except Exception as e:
            self.logger.error(f"Failed to fetch Stripe charges: {e}")
            raise

        # Fetch refunds
        try:
            refund_params = {"limit": 100}
            if since:
                refund_params["created"] = {"gte": int(since.timestamp())}

            refunds = stripe.Refund.list(**refund_params)
            for refund in refunds.auto_paging_iter():
                records.append({
                    "type": "refund",
                    "id": refund.id,
                    "amount": refund.amount,
                    "currency": refund.currency.upper(),
                    "description": f"Refund for charge {refund.charge}",
                    "created": refund.created,
                    "status": refund.status,
                    "metadata": {},
                    "charge_id": refund.charge,
                })
        except Exception as e:
            self.logger.error(f"Failed to fetch Stripe refunds: {e}")
            raise

        return records

    def normalize(self, raw_records: list[dict]) -> list[FinancialRecord]:
        """
        Convert Stripe records to FinancialRecords.

        Mapping:
        - Stripe charge (succeeded) → revenue
        - Stripe charge (failed) → skipped
        - Stripe refund → refund (negative amount)
        """
        normalized = []
        now = datetime.now(timezone.utc)

        for record in raw_records:
            record_type_str = record.get("type", "")

            if record_type_str == "charge":
                if record.get("status") != "succeeded":
                    continue  # Skip failed charges

                normalized.append(FinancialRecord(
                    tenant_id=self.tenant_id,
                    source="stripe",
                    source_id=record["id"],
                    record_type="revenue",
                    category="revenue",
                    amount_cents=record["amount"],  # Stripe already uses cents
                    currency=record["currency"],
                    description=record.get("description", ""),
                    occurred_at=datetime.fromtimestamp(
                        record["created"], tz=timezone.utc
                    ),
                    metadata_json={
                        "stripe_customer": record.get("customer"),
                        "stripe_metadata": record.get("metadata", {}),
                    },
                    synced_at=now,
                ))

            elif record_type_str == "refund":
                normalized.append(FinancialRecord(
                    tenant_id=self.tenant_id,
                    source="stripe",
                    source_id=record["id"],
                    record_type="refund",
                    category="refund",
                    amount_cents=-abs(record["amount"]),  # Refunds are negative
                    currency=record["currency"],
                    description=record.get("description", ""),
                    occurred_at=datetime.fromtimestamp(
                        record["created"], tz=timezone.utc
                    ),
                    metadata_json={
                        "stripe_charge_id": record.get("charge_id"),
                    },
                    synced_at=now,
                ))

        return normalized
