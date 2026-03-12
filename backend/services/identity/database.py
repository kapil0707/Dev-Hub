"""
=============================================================================
Identity Service — Database Layer
=============================================================================
PURPOSE:
    Sets up the async SQLAlchemy engine and provides a reusable DB session
    as a FastAPI dependency (injected into route handlers via Depends()).

ARCHITECTURE: WHY ASYNC?
    FastAPI is an async framework (runs on asyncio event loop).
    A synchronous DB driver would BLOCK the event loop during every query,
    killing the concurrency advantage of async entirely.

    asyncpg + SQLAlchemy async = queries are awaitable coroutines.
    The event loop can serve other requests while waiting for DB I/O.

    C++ analogy: async DB is like non-blocking I/O (epoll/IOCP) instead
    of blocking recv() — the thread isn't stuck waiting for the socket.

DEPENDENCY INJECTION PATTERN:
    FastAPI's Depends() creates a "scope" per request:
        @app.get("/me")
        async def get_me(db: AsyncSession = Depends(get_db)):
            # db is a fresh session, auto-closed after the response is sent
            ...
    This guarantees no session leaks, even if an exception is raised.
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
# pool_pre_ping=True: before handing out a connection from the pool,
# send a cheap "SELECT 1" to verify the connection is still alive.
# Without this, you get cryptic errors after the DB restarts.
# =============================================================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://devhub_user:devhub_password_local@localhost:5432/devhub_db",
)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,      # Set True temporarily to see all SQL statements in console
    pool_size=5,     # Max persistent connections (fine for local single-user dev)
    max_overflow=10, # Extra connections allowed when pool is exhausted
)

# =============================================================================
# Session Factory
# =============================================================================
# async_sessionmaker is the async equivalent of sessionmaker.
# expire_on_commit=False: after commit(), don't expire attributes.
# Without this, accessing model.id after commit() would trigger another DB query.
# =============================================================================
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session per request.

    Usage in a route:
        async def my_route(db: AsyncSession = Depends(get_db)):

    The 'finally' block ensures the session is always closed,
    even if the route raises an exception — preventing connection leaks.
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
