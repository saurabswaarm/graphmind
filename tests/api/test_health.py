import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test the basic health check endpoint."""
    response = await test_client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_check(test_client: AsyncClient):
    """Test the readiness check endpoint with database connection."""
    response = await test_client.get("/readyz")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_version_info(test_client: AsyncClient):
    """Test the version info endpoint."""
    response = await test_client.get("/version")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "version" in data
    assert "api" in data
    assert data["api"] == "Graph Service"
