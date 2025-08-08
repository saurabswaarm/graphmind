from typing import List, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    APP_ENV: str = "local"
    LOG_LEVEL: str = "info"

    # Database Configuration
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 10

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

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Optional[str | List[str]]) -> List[str]:
        """Parse CORS_ORIGINS from string to list if needed."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create global settings instance
settings = Settings()
