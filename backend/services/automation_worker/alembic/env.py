"""
=============================================================================
Alembic Environment — Automation Worker (SYNC driver version)
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
_alembic_dir = os.path.dirname(os.path.abspath(__file__))
_service_root = os.path.abspath(os.path.join(_alembic_dir, ".."))
_backend_root = os.path.abspath(os.path.join(_alembic_dir, "..", "..", ".."))
_monorepo_root = os.path.abspath(os.path.join(_alembic_dir, "..", "..", "..", ".."))

sys.path.insert(0, _service_root)   # for models
sys.path.insert(0, _backend_root)   # for devhub_shared

# Load .env from the monorepo root
load_dotenv(os.path.join(_monorepo_root, ".env"))

# =============================================================================
# Step 2: Import models so autogenerate can detect them
# =============================================================================
from devhub_shared.models.base import Base   # noqa: E402
from models import Execution                 # noqa: E402, F401

target_metadata = Base.metadata

# =============================================================================
# Step 3: Build SYNC database URL for Alembic
# =============================================================================
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
# Offline mode
# =============================================================================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="automation",
    )
    with context.begin_transaction():
        context.run_migrations()


# =============================================================================
# Online mode
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
            version_table_schema="automation",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
