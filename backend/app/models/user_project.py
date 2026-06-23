"""User-completed portfolio projects (drives experience level)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class UserProjectCompletion(BaseModel):
    __tablename__ = "user_project_completions"
    __table_args__ = (UniqueConstraint("user_id", "project_title", name="uq_user_project_title"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    project_title: Mapped[str] = mapped_column(String(255), nullable=False)
    career_slug: Mapped[str | None] = mapped_column(String(80), nullable=True)
