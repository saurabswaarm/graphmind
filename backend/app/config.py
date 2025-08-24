from typing import List, Optional, Union, Any
from pydantic import PostgresDsn, AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    APP_ENV: str = "local"
    LOG_LEVEL: str = "info"

    # Database Configuration
    DATABASE_URL: Union[PostgresDsn, AnyUrl]
    DB_POOL_SIZE: int = 10

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v: Any) -> str:
        """Support both PostgreSQL and SQLite URLs."""
        if isinstance(v, str):
            # Allow SQLite URLs for testing
            if v.startswith("sqlite"):
                return v
        return v

    # Web Server Configuration
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000
    UVICORN_WORKERS: int = 1

    # Graph Configuration
    ALLOW_SELF_RELATIONSHIPS: bool = False
    GRAPH_DEFAULT_LIMIT_NODES: int = 10000
    GRAPH_DEFAULT_LIMIT_EDGES: int = 20000

    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Special handling for test environment
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # For test environment, use default values if certain fields are causing issues
        if self.APP_ENV == "test":
            # Make sure we have sensible test defaults
            if not hasattr(self, "CORS_ORIGINS") or not self.CORS_ORIGINS:
                object.__setattr__(
                    self, "CORS_ORIGINS", ["http://localhost:3000", "http://localhost:8000"]
                )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Optional[str | List[str]]) -> List[str]:
        """Parse CORS_ORIGINS from string to list if needed."""
        # Print debug info
        print(f"CORS_ORIGINS value type: {type(v)}, value: {v}")

        if isinstance(v, str):
            if not v or v.lower() == "none":
                return []
            if not v.startswith("["):
                result = [i.strip() for i in v.split(",")]
                print(f"Parsed CORS_ORIGINS to: {result}")
                return result
        elif isinstance(v, list):
            return v
        elif v is None:
            return []

        # Default empty list
        return []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create global settings instance
settings = Settings()
