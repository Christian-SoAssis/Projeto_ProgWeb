"""bids

Revision ID: 007
Revises: 006
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "bids",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("estimated_hours", sa.Integer(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("request_id", "professional_id", name="uq_bids_request_professional"),
        sa.CheckConstraint("price_cents > 0", name="chk_bids_price"),
        sa.CheckConstraint("estimated_hours > 0", name="chk_bids_est_hours"),
        sa.CheckConstraint("status IN ('pending','accepted','rejected','cancelled')", name="chk_bids_status")
    )
    op.create_index("idx_bids_request_status", "bids", ["request_id", "status"])
    op.create_index("idx_bids_prof_created", "bids", ["professional_id", sa.text("created_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_bids_prof_created", table_name="bids")
    op.drop_index("idx_bids_request_status", table_name="bids")
    op.drop_table("bids")
