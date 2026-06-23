"""User model (Module 1 - Authentication)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile

OAuthProvider = ("local", "google", "github")


class User(BaseModel):
    """A registered TechMentor user.

    `password_hash` is nullable because OAuth-only users don't have one.
    `oauth_provider`/`oauth_subject` uniquely identify a remote identity.
    """

    __tablename__ = "users"

    public_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
        comment="Externally-exposed id (never the PK).",
    )
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    firebase_uid: Mapped[str | None] = mapped_column(
        String(128),
        unique=True,
        nullable=True,
        index=True,
        comment="Firebase Auth UID (primary external identity).",
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # OAuth linkage (one row per user, only one provider active at a time).
    oauth_provider: Mapped[str] = mapped_column(
        Enum(*OAuthProvider, name="oauth_provider_enum"),
        default="local",
        nullable=False,
    )
    oauth_subject: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # ---- Relationships ------------------------------------------------
    profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def full_name(self) -> str:
        return f"{self.firstname} {self.lastname}".strip()

    @property
    def has_password(self) -> bool:
        return self.password_hash is not None
