"""
=============================================================================
Blob Storage Service — Database Configuration
=============================================================================
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv

_service_root = os.path.dirname(os.path.abspath(__file__))
_monorepo_root = os.path.abspath(os.path.join(_service_root, "..", "..", ".."))
load_dotenv(os.path.join(_monorepo_root, ".env"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://devhub_user:devhub_password_local@localhost:5432/devhub_db"
)

# Create an async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create a sessionmaker factory for async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """
    Dependency to provide a database session for a specific request.
    Yields the session and ensures it's closed afterward.
    """
    async with AsyncSessionLocal() as session:
        yield session
