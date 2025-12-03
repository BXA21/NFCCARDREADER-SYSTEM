"""
Pytest configuration and fixtures for testing.
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base
from app.main import app
from httpx import AsyncClient


# Test database URL (use a separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://attendance_user:attendance_pass@localhost:5432/attendance_db_test"


@pytest.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create a test database session."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client():
    """Create a test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac



