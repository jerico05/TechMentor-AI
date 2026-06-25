"""linkedin, portfolio urls and user portfolio projects

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("student_profiles", sa.Column("linkedin_url", sa.String(500), nullable=True))
    op.add_column("student_profiles", sa.Column("portfolio_url", sa.String(500), nullable=True))

    op.create_table(
        "linkedin_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("profile_url", sa.String(500), nullable=False),
        sa.Column("headline", sa.String(500), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("experiences", sa.JSON(), nullable=True),
        sa.Column("education", sa.JSON(), nullable=True),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="processing", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_linkedin_analyses_user_id"),
    )
    op.create_index("ix_linkedin_analyses_user_id", "linkedin_analyses", ["user_id"])

    op.create_table(
        "user_portfolio_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("stack", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(40), server_default="web", nullable=False),
        sa.Column("status", sa.String(20), server_default="processing", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "url", name="uq_user_portfolio_project_url"),
    )
    op.create_index("ix_user_portfolio_projects_user_id", "user_portfolio_projects", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_portfolio_projects_user_id", table_name="user_portfolio_projects")
    op.drop_table("user_portfolio_projects")
    op.drop_index("ix_linkedin_analyses_user_id", table_name="linkedin_analyses")
    op.drop_table("linkedin_analyses")
    op.drop_column("student_profiles", "portfolio_url")
    op.drop_column("student_profiles", "linkedin_url")
