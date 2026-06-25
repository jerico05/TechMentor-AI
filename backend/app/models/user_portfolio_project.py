"""Portfolio projects added by the user (link + extraction)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel


class UserPortfolioProject(BaseModel):
    __tablename__ = "user_portfolio_projects"
    __table_args__ = (UniqueConstraint("user_id", "url", name="uq_user_portfolio_project_url"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack: Mapped[list | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="web", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="processing", nullable=False)
