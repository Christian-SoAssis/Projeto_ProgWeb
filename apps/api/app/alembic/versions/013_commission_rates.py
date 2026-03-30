"""commission_rates

Revision ID: 013
Revises: 012
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "commission_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=True),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.CheckConstraint("percent > 0 AND percent < 100", name="chk_comm_rates_percent"),
        sa.CheckConstraint("effective_until IS NULL OR effective_until > effective_from", name="chk_comm_rates_dates")
    )
    op.create_index("idx_comm_rates_cat_effective", "commission_rates", ["category_id", sa.text("effective_from DESC")])
    
    # Inline seed
    op.execute("INSERT INTO commission_rates (id, category_id, percent) VALUES (gen_random_uuid(), NULL, 5.00)")

def downgrade() -> None:
    op.execute("DELETE FROM commission_rates WHERE category_id IS NULL")
    op.drop_index("idx_comm_rates_cat_effective", table_name="commission_rates")
    op.drop_table("commission_rates")
