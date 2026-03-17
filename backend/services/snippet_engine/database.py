"""
=============================================================================
Snippet Engine — Database Layer
=============================================================================
PURPOSE:
    Sets up the async SQLAlchemy engine and provides a reusable DB session.
    Same pattern as the Identity Service — consistency across all services.

    The Snippet Engine uses gRPC (not FastAPI), so get_db() is called
    directly in the gRPC servicer methods, NOT via FastAPI's Depends().

DRIVER: asyncpg (async) for the gRPC server runtime.
        psycopg2 (sync) for Alembic migrations (configured in alembic/env.py).
=============================================================================
"""
import os
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv("../../../.env")

# =============================================================================
# Engine — the connection pool
# =============================================================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://devhub_user:devhub_password_local@localhost:5433/devhub_db",
)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

# =============================================================================
# Session Factory
# =============================================================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an async database session. Used directly in gRPC servicer methods:

        async with get_db() as session:
            ...

    Or as an async generator:
        async for session in get_db():
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
