"""Mock configuration for testing."""

from typing import List


class MockSettings:
    """Mock settings for tests."""
    
    # Application Configuration
    APP_ENV: str = "test"
    LOG_LEVEL: str = "INFO"

    # Database Configuration (using SQLite for tests)
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


# Create a mock settings instance
mock_settings = MockSettings()


# Create a module-level patch for tests
def patch_app_config():
    """Patch the app configuration for tests."""
    import sys
    from unittest.mock import MagicMock
    
    # Create a mock module for app.config
    mock_module = MagicMock()
    mock_module.settings = mock_settings
    
    # Replace the real module with our mock in sys.modules
    sys.modules["app.config"] = mock_module
    
    return mock_settings
