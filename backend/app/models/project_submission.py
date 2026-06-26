"""Project submission proof-of-work model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class ProjectSubmission(BaseModel):
    __tablename__ = "project_submissions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_title: Mapped[str] = mapped_column(String(255), nullable=False)
    career_slug: Mapped[str | None] = mapped_column(String(80), nullable=True)

    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # pending | approved | rejected
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    evaluation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
