"""
=============================================================================
Identity Service — User ORM Model
=============================================================================
PURPOSE:
    Defines the `users` table structure as a Python class.
    SQLAlchemy maps this class ↔ the database table bidirectionally:
    - Python object → SQL INSERT/UPDATE
    - SQL row → Python object (via SELECT)

TABLE: identity.users   (schema "identity" maps to the schema we created in init-db.sql)

DESIGN DECISIONS:
    - UUID primary key (not auto-increment integer): see shared/models/base.py
    - Password HASH stored, never the raw password
    - avatar_url is nullable — we don't have a file upload yet in Phase 1
    - is_active flag allows "soft banning" without deleting the user row
=============================================================================
"""
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from devhub_shared.models.base import Base, TimestampMixin, new_uuid


class User(Base, TimestampMixin):
    """
    ORM model for the identity.users table.

    Inherits:
        Base         → registers with SQLAlchemy metadata (needed by Alembic)
        TimestampMixin → auto-adds created_at + updated_at columns
    """
    __tablename__ = "users"
    __table_args__ = (
        # __table_args__ tuple form allows mixing constraints + dict options
        sa.UniqueConstraint("email", name="uq_users_email"),
        {"schema": "identity"},  # ← maps to PostgreSQL schema "identity"
    )

    # --- Primary Key ---------------------------------------------------------
    # server_default is used for DB-level default (used by Alembic test data).
    # Python-side default (new_uuid) is used when creating objects in code.
    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=new_uuid,
    )

    # --- Core Fields ---------------------------------------------------------
    email: Mapped[str] = mapped_column(
        sa.String(254),   # 254 = RFC 5321 max email length
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )

    # WHY store a "hash" and not the password?
    # Argon2 produces a self-describing hash string like:
    #   "$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>"
    # Even if the DB is leaked, an attacker cannot reverse this to the password.
    # The hash string is ~100 chars — VARCHAR(255) safely covers it.
    password_hash: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )

    # Optional fields
    avatar_url: Mapped[str | None] = mapped_column(
        sa.String(500),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=True,
        nullable=False,
        server_default=sa.true(),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
