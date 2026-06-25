"""Student profile model (Module 2 - Profil Étudiant)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User

AcademicLevel = ("licence1", "licence2", "licence3", "master1", "master2", "other")


class StudentProfile(BaseModel):
    """Academic & career context filled by the student.

    One profile per user (1-1). `career_goal` is free-text at this stage and is
    later resolved to a `career_path_id` (Module 6) during analysis.
    """

    __tablename__ = "student_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    university: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    academic_level: Mapped[str] = mapped_column(
        Enum(*AcademicLevel, name="academic_level_enum"),
        default="licence3",
        nullable=False,
    )
    career_goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    career_path_id: Mapped[int | None] = mapped_column(
        ForeignKey("career_paths.id", ondelete="SET NULL"),
        nullable=True,
    )
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- Relationships ------------------------------------------------
    user: Mapped["User"] = relationship(back_populates="profile")
