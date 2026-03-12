"""
=============================================================================
Alembic Environment — Identity Service (SYNC driver version)
=============================================================================
ARCHITECTURE NOTE: Why psycopg2 for migrations, asyncpg for the app?

    Alembic is a CLI tool — it runs synchronously. There is zero benefit to
    using an async driver in Alembic because no event loop is running.
    Using asyncpg in Alembic just adds complexity with no gain.

    The FastAPI app uses asyncpg at RUNTIME because:
    - FastAPI's async handlers need non-blocking I/O
    - asyncpg is 3-5x faster than psycopg2 in async workloads

    This dual-driver pattern is the STANDARD production approach:
        Alembic CLI → psycopg2 (sync, simple, reliable)
        FastAPI app → asyncpg (async, high performance)

    Both drivers talk to the same PostgreSQL database and schema.

AUTOGENERATE:
    `alembic revision --autogenerate -m "description"`
    Compares Python models (registered in target_metadata) vs live DB schema.
    Generates upgrade()/downgrade() SQL in alembic/versions/

APPLY:
    `alembic upgrade head` — runs all pending migrations
    `alembic downgrade -1`  — rolls back the last migration
=============================================================================
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# =============================================================================
# Step 1: Add shared and service packages to import path
# =============================================================================
# This file lives at:  backend/services/identity/alembic/env.py
# Shared package at:   backend/shared/
# Service root at:     backend/services/identity/
_alembic_dir = os.path.dirname(os.path.abspath(__file__))
_service_root = os.path.abspath(os.path.join(_alembic_dir, ".."))
_backend_root = os.path.abspath(os.path.join(_alembic_dir, "..", "..", ".."))
_monorepo_root = os.path.abspath(os.path.join(_alembic_dir, "..", "..", "..", ".."))

sys.path.insert(0, _service_root)   # for `from models import User`
sys.path.insert(0, _backend_root)   # for `from devhub_shared...`

# Load .env from the monorepo root (absolute path — works from any working dir)
load_dotenv(os.path.join(_monorepo_root, ".env"))

# =============================================================================
# Step 2: Import models so autogenerate can detect them
# =============================================================================
from devhub_shared.models.base import Base   # noqa: E402
from models import User                       # noqa: E402, F401

target_metadata = Base.metadata

# =============================================================================
# Step 3: Build SYNC database URL for Alembic
# =============================================================================
# Take the asyncpg URL and replace driver with psycopg2 (sync)
# asyncpg URL:  postgresql+asyncpg://user:pass@host/db
# psycopg2 URL: postgresql+psycopg2://user:pass@host/db  (or just postgresql://)
_async_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://devhub_user:devhub_password_local@localhost:5432/devhub_db",
)
SYNC_DATABASE_URL = _async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


# =============================================================================
# Offline mode — generate SQL script without connecting to DB
# =============================================================================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="identity",
    )
    with context.begin_transaction():
        context.run_migrations()


# =============================================================================
# Online mode — connect to DB and run migrations directly
# =============================================================================
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="identity",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
