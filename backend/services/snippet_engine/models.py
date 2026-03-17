"""
=============================================================================
Snippet Engine — Snippet ORM Model
=============================================================================
TABLE: snippets.snippets

DESIGN:
    - UUID primary key (same as Identity Service for consistency)
    - user_id references the owner (no FK constraint across schemas — each
      service owns its own schema; cross-service integrity is application-level)
    - tags stored as ARRAY(String) — PostgreSQL native array type.
      Perfect for simple tag lists. If tags needed their own metadata
      (description, color), we'd use a junction table instead.
    - code stored as TEXT — no length limit for code content
=============================================================================
"""
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from devhub_shared.models.base import Base, TimestampMixin, new_uuid


class Snippet(Base, TimestampMixin):
    """
    ORM model for the snippets.snippets table.

    Inherits:
        Base         → registers with SQLAlchemy metadata (needed by Alembic)
        TimestampMixin → auto-adds created_at + updated_at columns
    """
    __tablename__ = "snippets"
    __table_args__ = (
        {"schema": "snippets"},  # ← maps to PostgreSQL schema "snippets"
    )

    # --- Primary Key ---------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=new_uuid,
    )

    # --- Owner ---------------------------------------------------------------
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        nullable=False,
        index=True,  # frequently queried — list all snippets for a user
    )

    # --- Content Fields ------------------------------------------------------
    title: Mapped[str] = mapped_column(
        sa.String(200),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        sa.String(50),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
    )

    # Tags as PostgreSQL ARRAY — efficient for filtering with ANY/CONTAINS
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(sa.String(50)),
        nullable=True,
        default=list,
    )

    def __repr__(self) -> str:
        return f"<Snippet id={self.id} title={self.title!r} lang={self.language}>"
