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


@pytest_asyncio.fixture
async def async_client():
    """Create an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def api_headers():
    """Default headers for authenticated requests."""
    return {
        "Content-Type": "application/json",
        "X-API-Key": "test_key_123",
    }
