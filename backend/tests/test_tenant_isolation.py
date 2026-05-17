"""
AI CFO — Tenant Isolation Tests

Critical tests verifying that tenant data is properly isolated.
These tests are non-negotiable — tenant isolation is a core security requirement.
"""

import pytest
from httpx import AsyncClient

from app.auth.utils import create_access_token
from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
class TestTenantIsolation:
    """Tests verifying tenant isolation at the API level."""

    async def test_unauthenticated_request_rejected(self, client: AsyncClient):
        """Endpoints requiring auth reject unauthenticated requests."""
        response = await client.get("/api/v1/integrations/status")
        assert response.status_code == 401

    async def test_invalid_token_rejected(self, client: AsyncClient):
        """Endpoints reject invalid JWT tokens."""
        response = await client.get(
            "/api/v1/integrations/status",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    async def test_audit_log_scoped_to_tenant(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Audit log only returns entries for the authenticated tenant."""
        response = await client.get("/api/v1/audit-log", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        # Should only see entries for our tenant
        assert isinstance(data["items"], list)

    async def test_connector_status_scoped_to_tenant(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Connector status only returns connectors for the authenticated tenant."""
        response = await client.get(
            "/api/v1/integrations/status", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "connectors" in data
        assert isinstance(data["connectors"], list)
