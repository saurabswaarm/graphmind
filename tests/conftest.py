import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

# Apply mock configuration patch BEFORE importing any app modules
from tests.mock_config import patch_app_config

# Patch the app configuration
mock_settings = patch_app_config()

import pytest
import pytest_asyncio
from fastapi import FastAPI, APIRouter
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Import our test utilities
from tests.db_utils import test_engine, get_test_db

# Now we can safely import app modules
from app.models.base import Base

# Import router modules
from app.api import health, entities, relationships, graph
from app.api.errors import register_exception_handlers


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def init_db():
    """Initialize the test database."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_engine
    
    # Clean up
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(init_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh test database session for a test."""
    from tests.db_utils import TestSessionLocal
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
        # Clean tables after each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(f"DELETE FROM {table.name}")
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_app(test_db) -> FastAPI:
    """Create a test app with the test database."""
    # Create a test FastAPI app directly instead of using create_app()
    app = FastAPI(
        title="Graph API Test",
        description="Test instance of the Graph API",
        version="0.1.0",
    )
    
    # Create API router
    api_router = APIRouter()
    
    # Include all routers
    api_router.include_router(health.router, tags=["health"])
    api_router.include_router(entities.router, prefix="/entities", tags=["entities"])
    api_router.include_router(relationships.router, prefix="/relationships", tags=["relationships"])
    api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
    
    # Add API router to app
    app.include_router(api_router)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Override the database dependency with our test db
    # Import this here to avoid circular imports
    from app.db.session import get_db
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    return app


@pytest_asyncio.fixture(scope="function")
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the app."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
