"""Add quizzes table for persisted quiz sessions.

Revision ID: 0005
Revises: 0004
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("quiz_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("career_path_id", sa.Integer(), nullable=False),
        sa.Column("questions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["career_path_id"], ["career_paths.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_quizzes")),
        sa.UniqueConstraint("quiz_id", name=op.f("uq_quizzes_quiz_id")),
    )
    op.create_index(op.f("ix_quizzes_quiz_id"), "quizzes", ["quiz_id"], unique=False)
    op.create_index(op.f("ix_quizzes_user_id"), "quizzes", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_quizzes_user_id"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_quiz_id"), table_name="quizzes")
    op.drop_table("quizzes")
