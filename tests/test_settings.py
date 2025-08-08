"""Test settings for the application."""

from pydantic import AnyUrl
from typing import List, Optional, Any

# A simplified settings class for tests that doesn't rely on environment variables
class TestSettings:
    """Test settings that bypass environment variable loading."""
    
    # Application Configuration
    APP_ENV: str = "test"
    LOG_LEVEL: str = "INFO"

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    DB_POOL_SIZE: int = 5

    # Web Server Configuration
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    UVICORN_WORKERS: int = 1

    # Graph Configuration
    ALLOW_SELF_RELATIONSHIPS: bool = False
    GRAPH_DEFAULT_LIMIT_NODES: int = 1000
    GRAPH_DEFAULT_LIMIT_EDGES: int = 5000

    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

# Create global test settings instance
test_settings = TestSettings()
