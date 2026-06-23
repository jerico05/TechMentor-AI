"""Add composite indexes for common user-scoped queries.

Revision ID: 0006
Revises: 0005
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_analysis_history_user_id_created_at",
        "analysis_history",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_cv_files_user_id_created_at",
        "cv_files",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_roadmaps_user_id_status_created_at",
        "roadmaps",
        ["user_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_chat_sessions_user_id_updated_at",
        "chat_sessions",
        ["user_id", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_sessions_user_id_updated_at", table_name="chat_sessions")
    op.drop_index("ix_roadmaps_user_id_status_created_at", table_name="roadmaps")
    op.drop_index("ix_cv_files_user_id_created_at", table_name="cv_files")
    op.drop_index("ix_analysis_history_user_id_created_at", table_name="analysis_history")
