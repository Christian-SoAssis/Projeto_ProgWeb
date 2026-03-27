"""create categories table

Revision ID: 002
Revises: 001
Create Date: 2026-03-27 10:05:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#1a9878"),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )

    op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_index("ix_categories_parent", "categories", ["parent_id"])

    # Constraint: validar formato hex da cor (#RRGGBB)
    op.create_check_constraint(
        "chk_categories_color_format",
        "categories",
        "color ~ '^#[0-9a-fA-F]{6}$'",
    )


def downgrade() -> None:
    op.drop_constraint("chk_categories_color_format", "categories", type_="check")
    op.drop_index("ix_categories_parent", table_name="categories")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
