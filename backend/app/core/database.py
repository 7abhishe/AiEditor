"""
CodeGenie AI Editor — Database Engine & Session
Configures SQLAlchemy async engine and provides session dependency.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ── Engine ───────────────────────────────────────────────
# Configure engine based on database type
# Use async_database_url which auto-converts postgresql:// to postgresql+asyncpg://
db_url = settings.async_database_url
is_sqlite = db_url.startswith("sqlite")

if is_sqlite:
    # SQLite: local development
    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL: production with connection pooling
    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

# ── Session Factory ──────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ───────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ── Dependency ───────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
