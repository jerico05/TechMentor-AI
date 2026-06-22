"""create users and student_profiles

Revision ID: 0001
Revises:
Create Date: 2026-06-22 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- users ----
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", sa.String(length=36), nullable=False, comment="Externally-exposed id (never the PK)."),
        sa.Column("firstname", sa.String(length=80), nullable=False),
        sa.Column("lastname", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "oauth_provider",
            sa.Enum("local", "google", "github", name="oauth_provider_enum"),
            nullable=False,
            server_default="local",
        ),
        sa.Column("oauth_subject", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("public_id", name=op.f("uq_users_public_id")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"])
    op.create_index(op.f("ix_users_oauth_subject"), "users", ["oauth_subject"])

    # ---- student_profiles ----
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("university", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column(
            "academic_level",
            sa.Enum("licence1", "licence2", "licence3", "master1", "master2", "other", name="academic_level_enum"),
            nullable=False,
            server_default="licence3",
        ),
        sa.Column("career_goal", sa.String(length=255), nullable=True),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE", name=op.f("fk_student_profiles_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_student_profiles")),
        sa.UniqueConstraint("user_id", name=op.f("uq_student_profiles_user_id")),
    )
    op.create_index(op.f("ix_student_profiles_user_id"), "student_profiles", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_student_profiles_user_id"), table_name="student_profiles")
    op.drop_table("student_profiles")
    op.drop_index(op.f("ix_users_oauth_subject"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    sa.Enum(name="academic_level_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="oauth_provider_enum").drop(op.get_bind(), checkfirst=True)
