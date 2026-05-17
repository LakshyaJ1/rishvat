"""
AI CFO — Connector Schemas

Pydantic models for integration connector endpoints.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    """Request to connect a new integration."""
    provider: str = Field(..., pattern="^(stripe|plaid|quickbooks|xero|razorpay)$")
    credentials: dict  # Provider-specific credentials


class ConnectorStatusResponse(BaseModel):
    """Status of a single connector."""
    id: uuid.UUID
    provider: str
    status: str
    permissions: str
    last_synced_at: datetime | None
    sync_error: str | None

    model_config = {"from_attributes": True}


class ConnectorListResponse(BaseModel):
    """List of all connectors for a tenant."""
    connectors: list[ConnectorStatusResponse]


class SyncResponse(BaseModel):
    """Response when triggering a manual sync."""
    task_id: str
    status: str = "queued"
