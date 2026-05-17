"""
AI CFO — Tenant Schema

Pydantic models for tenant data.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel


class TenantResponse(BaseModel):
    """Tenant information response."""
    id: uuid.UUID
    name: str
    slug: str
    jurisdiction: str
    autopilot_level: str
    shadow_mode_until: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
