"""user project completions table

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_project_completions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_title", sa.String(255), nullable=False),
        sa.Column("career_slug", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "project_title", name="uq_user_project_title"),
    )
    op.create_index("ix_user_project_completions_user_id", "user_project_completions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_user_project_completions_user_id", table_name="user_project_completions")
    op.drop_table("user_project_completions")
