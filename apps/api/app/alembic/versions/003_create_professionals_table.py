"""create professionals table

Revision ID: 003
Revises: 002
Create Date: 2026-03-27 14:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "professionals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("service_radius_km", sa.Float(), nullable=False, server_default="20"),
        sa.Column("hourly_rate_cents", sa.Integer(), nullable=True),
        sa.Column("reputation_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        sa.Column("document_path", sa.String(500), nullable=True),
        sa.Column("document_type", sa.String(10), nullable=True),
    )

    op.create_index("ix_professionals_user_id", "professionals", ["user_id"])
    op.create_index("ix_professionals_is_verified", "professionals", ["is_verified"])


def downgrade() -> None:
    op.drop_index("ix_professionals_is_verified", table_name="professionals")
    op.drop_index("ix_professionals_user_id", table_name="professionals")
    op.drop_table("professionals")
