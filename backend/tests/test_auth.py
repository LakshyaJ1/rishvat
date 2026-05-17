"""
AI CFO — Auth Endpoint Tests

Tests for registration, login, and token refresh.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegistration:
    """Tests for POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """A new user can register and receives tokens."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "founder@startup.com",
                "password": "SecurePass123!",
                "full_name": "Jane Founder",
                "company_name": "My Startup",
                "jurisdiction": "US",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "founder@startup.com"
        assert data["user"]["role"] == "founder"
        assert data["user"]["tenant_id"] is not None

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Registering with an existing email fails."""
        payload = {
            "email": "duplicate@startup.com",
            "password": "SecurePass123!",
            "full_name": "Jane Founder",
            "company_name": "Startup One",
            "jurisdiction": "US",
        }
        # First registration
        await client.post("/api/v1/auth/register", json=payload)

        # Duplicate
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_short_password(self, client: AsyncClient):
        """Registration with a password under 8 characters is rejected."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@startup.com",
                "password": "short",
                "full_name": "Jane Founder",
                "company_name": "My Startup",
            },
        )
        assert response.status_code == 422  # Pydantic validation


@pytest.mark.asyncio
class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    async def test_login_success(self, client: AsyncClient):
        """A registered user can log in."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@startup.com",
                "password": "SecurePass123!",
                "full_name": "Jane Founder",
                "company_name": "Login Startup",
            },
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@startup.com", "password": "SecurePass123!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "login@startup.com"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Login with wrong password fails."""
        # Register
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@startup.com",
                "password": "SecurePass123!",
                "full_name": "Jane Founder",
                "company_name": "Wrong Pass Startup",
            },
        )

        # Wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@startup.com", "password": "WrongPassword!"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with non-existent email fails."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@startup.com", "password": "SomePass123!"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestTokenRefresh:
    """Tests for POST /api/v1/auth/refresh"""

    async def test_refresh_success(self, client: AsyncClient):
        """A valid refresh token produces new tokens."""
        # Register to get tokens
        reg_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "refresh@startup.com",
                "password": "SecurePass123!",
                "full_name": "Jane Founder",
                "company_name": "Refresh Startup",
            },
        )
        refresh_token = reg_response.json()["refresh_token"]

        # Refresh
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """An invalid refresh token is rejected."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401
