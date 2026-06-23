"""Skills & career paths (Modules 6-7)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel


class Skill(BaseModel):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=10, nullable=False)


class CareerPath(BaseModel):
    __tablename__ = "career_paths"

    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    skills: Mapped[list["CareerPathSkill"]] = relationship(back_populates="career_path", lazy="selectin")


class CareerPathSkill(BaseModel):
    __tablename__ = "career_path_skills"
    __table_args__ = (UniqueConstraint("career_path_id", "skill_id", name="uq_career_path_skill"),)

    career_path_id: Mapped[int] = mapped_column(ForeignKey("career_paths.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    career_path: Mapped["CareerPath"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(lazy="joined")


class UserSkill(BaseModel):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=80, nullable=False)

    skill: Mapped["Skill"] = relationship(lazy="joined")
