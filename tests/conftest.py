import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import create_app
from app.models.base import Base
from app.db.session import get_db

# Test database URL - using SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test engine for the database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh test database session for a test."""
    # Create a session factory bound to the test engine
    test_async_session = async_sessionmaker(
        test_engine, expire_on_commit=False, autoflush=False
    )
    
    async with test_async_session() as session:
        yield session
        await session.rollback()
        # Clean tables after each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(f"DELETE FROM {table.name}")
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_app(test_db) -> FastAPI:
    """Create a test app with the test database."""
    # Override the get_db dependency
    app = create_app()
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app


@pytest_asyncio.fixture(scope="function")
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the app."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
