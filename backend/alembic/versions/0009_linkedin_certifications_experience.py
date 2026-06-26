"""Add certifications and total experience years to linkedin_analyses.

Revision ID: 0009
Revises: 0008
Create Date: 2026-06-26
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("linkedin_analyses", sa.Column("certifications", sa.JSON(), nullable=True))
    op.add_column(
        "linkedin_analyses",
        sa.Column("total_experience_years", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("linkedin_analyses", "total_experience_years")
    op.drop_column("linkedin_analyses", "certifications")
