"""Analysis history, roadmaps & quiz (Modules 8–12, 15)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class AnalysisHistory(BaseModel):
    __tablename__ = "analysis_history"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    career_path_id: Mapped[int] = mapped_column(ForeignKey("career_paths.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    owned_skills: Mapped[list] = mapped_column(JSON, nullable=False)
    missing_skills: Mapped[list] = mapped_column(JSON, nullable=False)


class Roadmap(BaseModel):
    __tablename__ = "roadmaps"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    career_path_id: Mapped[int] = mapped_column(ForeignKey("career_paths.id"), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class QuizAttempt(BaseModel):
    __tablename__ = "quiz_attempts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    career_path_id: Mapped[int] = mapped_column(ForeignKey("career_paths.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
