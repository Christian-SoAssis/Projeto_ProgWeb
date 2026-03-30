"""professional_categories

Revision ID: 004
Revises: 003
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "professional_categories",
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.CheckConstraint("years_experience >= 0", name="chk_prof_cat_experience")
    )
    op.create_index("idx_prof_cat_category_id", "professional_categories", ["category_id"])

def downgrade() -> None:
    op.drop_index("idx_prof_cat_category_id", table_name="professional_categories")
    op.drop_table("professional_categories")
