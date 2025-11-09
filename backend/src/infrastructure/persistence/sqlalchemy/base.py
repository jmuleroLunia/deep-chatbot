"""SQLAlchemy base configuration."""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Database URLs
DATABASE_URL = "sqlite+aiosqlite:///./workspace/threads.db"
SYNC_DATABASE_URL = "sqlite:///./workspace/threads.db"

# Async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Sync engine (for backward compatibility with tools)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    future=True,
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Sync session factory (for backward compatibility)
SyncSessionFactory = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# Base class for ORM models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.

    Usage with FastAPI:
        async def endpoint(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize database by creating all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """Close database connections."""
    await async_engine.dispose()
