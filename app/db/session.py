from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from ..config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async support
# This ensures we're using the asyncpg driver instead of psycopg2
database_url_str = str(settings.DATABASE_URL)
if database_url_str.startswith("postgresql://"):
    database_url_str = database_url_str.replace("postgresql://", "postgresql+asyncpg://")

# Create engine with connection pool
engine = create_async_engine(
    database_url_str,
    pool_size=settings.DB_POOL_SIZE,
    pool_pre_ping=True,
    echo=settings.APP_ENV == "local",
)

# Create session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Yields a new session for each request and ensures proper cleanup.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
