"""
CodeGenie AI Editor — Test Fixtures
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db


# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

# Create a specific engine for testing
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Override the app's database dependency
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database tables before all tests, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """Create an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def api_headers(async_client):
    """Register a test user and get a JWT token for headers."""
    # 1. Register
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    # 2. Login
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "securepassword"},
    )
    token = login_resp.json()["access_token"]
    
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
