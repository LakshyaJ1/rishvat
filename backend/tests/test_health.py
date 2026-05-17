"""
AI CFO — Health Endpoint Tests

Tests for GET /health and GET /metrics.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealth:
    """Tests for GET /api/v1/health"""

    async def test_health_returns_status(self, client: AsyncClient):
        """Health endpoint returns service status."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "db" in data

    async def test_health_db_connected(self, client: AsyncClient):
        """Health endpoint shows DB as OK when connected."""
        response = await client.get("/api/v1/health")
        data = response.json()
        assert data["db"] == "ok"


@pytest.mark.asyncio
class TestMetrics:
    """Tests for GET /api/v1/metrics"""

    async def test_metrics_returns_counts(self, client: AsyncClient):
        """Metrics endpoint returns operational counts."""
        response = await client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "active_tenants" in data
        assert "total_records" in data
        assert "uptime_seconds" in data
