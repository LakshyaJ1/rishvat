"""
AI CFO — Base Connector

Abstract base class that all integration connectors must implement.
Every connector must:
1. Implement fetch() to pull data from the external API
2. Implement normalize() to convert external data to FinancialRecord objects
3. Be read-only by default

This is the integration contract. New connectors (QuickBooks, Xero, Razorpay)
will follow this exact pattern.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.models.financial_record import FinancialRecord

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Abstract base connector for all external integrations.

    Every connector:
    - Has a provider name (e.g., 'stripe', 'plaid')
    - Accepts decrypted credentials
    - Fetches raw data from the external API
    - Normalizes raw data into FinancialRecord objects
    - Is read-only by default
    """

    provider: str = ""

    def __init__(self, tenant_id: UUID, credentials: dict):
        self.tenant_id = tenant_id
        self.credentials = credentials
        self.logger = logging.getLogger(f"aicfo.connector.{self.provider}")

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> list[dict]:
        """
        Fetch raw data from the external API.

        Args:
            since: Only fetch records created/updated after this timestamp.
                   None means fetch all available data.

        Returns:
            List of raw records from the external API.
        """
        ...

    @abstractmethod
    def normalize(self, raw_records: list[dict]) -> list[FinancialRecord]:
        """
        Convert raw API records into canonical FinancialRecord objects.

        This is where the magic happens — every connector maps its
        proprietary data format into our shared internal schema.

        Args:
            raw_records: Raw records from fetch()

        Returns:
            List of FinancialRecord objects ready for database insertion.
        """
        ...

    async def sync(self, since: datetime | None = None) -> list[FinancialRecord]:
        """
        Full sync pipeline: fetch + normalize.
        This is the method called by Celery tasks.
        """
        self.logger.info(
            f"Starting sync for tenant {self.tenant_id} "
            f"(since={since})"
        )

        try:
            raw_records = await self.fetch(since=since)
            self.logger.info(f"Fetched {len(raw_records)} raw records")

            normalized = self.normalize(raw_records)
            self.logger.info(f"Normalized into {len(normalized)} records")

            return normalized

        except Exception as e:
            self.logger.error(f"Sync failed: {e}", exc_info=True)
            raise

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Test that the stored credentials are valid.
        Called during initial connection setup.
        """
        ...
