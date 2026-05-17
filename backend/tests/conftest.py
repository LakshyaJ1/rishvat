"""
AI CFO — Test Fixtures

Provides test database, client, and authenticated user fixtures.
Uses an in-memory or test PostgreSQL database.
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.utils import create_access_token, hash_password
from app.config import get_settings
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.user import User

# Use a test database URL
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://aicfo:aicfo_dev_password@localhost:5432/aicfo_test",
)

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    Creates all tables before the test and drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test HTTP client that uses the test database session.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Startup",
        slug=f"test-startup-{uuid.uuid4().hex[:8]}",
        jurisdiction="US",
        shadow_mode_until=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test user belonging to the test tenant."""
    user = User(
        email=f"test-{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Test Founder",
        role="founder",
        tenant_id=test_tenant.id,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
def auth_headers(test_user: User, test_tenant: Tenant) -> dict:
    """Generate auth headers with a valid JWT token."""
    token = create_access_token(
        user_id=test_user.id,
        tenant_id=test_tenant.id,
        role=test_user.role,
    )
    return {"Authorization": f"Bearer {token}"}
