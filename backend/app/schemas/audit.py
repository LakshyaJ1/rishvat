"""
AI CFO — Audit Log Schemas

Pydantic models for audit log API responses.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Single audit log entry response."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None
    action_type: str
    action_detail: dict | None
    data_sources: dict | None
    outcome: str
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
