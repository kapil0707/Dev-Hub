"""
=============================================================================
SQLAlchemy Base Model — devhub_shared.models.base
=============================================================================
PURPOSE:
    Provides a shared DeclarativeBase and a reusable TimestampMixin that
    ALL service models inherit from. This ensures:
    - Consistent column naming conventions across services
    - UUID primary keys (not integer IDs) — more secure and portable
    - created_at / updated_at on every table automatically

WHY UUID PRIMARY KEYS (not integers)?
    Integer IDs are sequential and predictable: /snippets/1, /snippets/2...
    This leaks row count information and allows enumeration attacks.
    UUIDs like /snippets/550e8400-e29b-41d4-a716-446655440000 are:
    - Non-guessable
    - Safe to expose in public URLs
    - Collision-resistant across distributed systems (no central counter needed)

USAGE (in any service's models.py):
    from devhub_shared.models.base import Base, TimestampMixin
    import sqlalchemy as sa

    class User(Base, TimestampMixin):
        __tablename__ = "users"
        __table_args__ = {"schema": "identity"}

        id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
        email = sa.Column(sa.String, unique=True, nullable=False)
=============================================================================
"""
import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class Base(DeclarativeBase):
    """
    The single shared declarative base for ALL Dev-Hub service models.
    Every service's ORM models must inherit from this class.

    WHY one shared Base?
    Alembic needs to discover models for autogenerate to work.
    By using one Base across all services, each service's alembic/env.py
    can import just its own models and Alembic will correctly diff them.
    """
    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at columns to any model.

    Use this on every table — it's almost always needed and costs nothing.
    'updated_at' uses onupdate=datetime.now to auto-refresh on SQL UPDATE.
    """
    created_at: MappedColumn[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


def new_uuid() -> uuid.UUID:
    """Helper function to generate a new UUID v4. Use as column default."""
    return uuid.uuid4()
