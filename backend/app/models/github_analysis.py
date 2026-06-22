"""GitHub analysis model (Module 5)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class GitHubAnalysis(BaseModel):
    __tablename__ = "github_analyses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    repo_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    languages: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    technologies: Mapped[list | None] = mapped_column(JSON, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing", nullable=False)
