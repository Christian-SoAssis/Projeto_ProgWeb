"""notifications

Revision ID: 011
Revises: 010
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("type IN ('bid_received','bid_accepted','bid_rejected','payment_confirmed','payout_completed','new_message','review_request','dispute_opened','dispute_response','dispute_resolved','professional_verified','professional_rejected','account_warning')", name="chk_notifications_type")
    )
    op.create_index("idx_notifications_user_unread", "notifications", ["user_id", sa.text("created_at DESC")], postgresql_where=sa.text("read_at IS NULL"))

def downgrade() -> None:
    op.drop_index("idx_notifications_user_unread", table_name="notifications", postgresql_where=sa.text("read_at IS NULL"))
    op.drop_table("notifications")
