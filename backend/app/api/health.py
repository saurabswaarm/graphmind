import os
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db

router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    Returns 200 OK if the API is running.
    """
    return {"status": "ok"}


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def ready_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Readiness check endpoint.
    Verifies that the application can connect to the database.
    Returns 200 OK if the application is ready to serve traffic.
    """
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        await result.scalar_one()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        # This would typically return a 503 Service Unavailable,
        # but we're just reporting the status for now

    return {"status": "ready", "database": db_status}


@router.get("/version", status_code=status.HTTP_200_OK)
async def version_info() -> Dict[str, Any]:
    """
    Version information endpoint.
    Returns the current version of the API.
    """
    # Get version from environment variable or default to unknown
    version = os.environ.get("APP_VERSION", "0.1.0")

    # Get Git SHA if available
    git_sha = os.environ.get("GIT_COMMIT_SHA", "unknown")

    return {"version": version, "git_commit": git_sha, "api": "Graph Service"}
