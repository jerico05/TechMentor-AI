"""LinkedIn profile analysis."""

from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class LinkedInAnalysis(BaseModel):
    __tablename__ = "linkedin_analyses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    profile_url: Mapped[str] = mapped_column(String(500), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(500), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    experiences: Mapped[list | None] = mapped_column(JSON, nullable=True)
    education: Mapped[list | None] = mapped_column(JSON, nullable=True)
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="processing", nullable=False)
