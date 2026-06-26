"""Add project_submissions table for proof-of-work evaluation.

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-26
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_title", sa.String(255), nullable=False),
        sa.Column("career_slug", sa.String(80), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("evaluation_score", sa.Integer(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_project_submissions_user_id", "project_submissions", ["user_id"])
    op.create_index(
        "ix_project_submissions_user_title",
        "project_submissions",
        ["user_id", "project_title"],
    )

    op.add_column(
        "user_project_completions",
        sa.Column("submission_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_project_completions", "submission_id")
    op.drop_index("ix_project_submissions_user_title", table_name="project_submissions")
    op.drop_index("ix_project_submissions_user_id", table_name="project_submissions")
    op.drop_table("project_submissions")
