"""disputes

Revision ID: 012
Revises: 011
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "disputes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("opened_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("evidence_urls", postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column("status", sa.Text(), nullable=False, server_default="opened"),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("refund_percent", sa.Integer(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("response_message", sa.Text(), nullable=True),
        sa.Column("response_evidence_urls", postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column("proposed_resolution", sa.Text(), nullable=True),
        sa.Column("response_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("length(reason) >= 10", name="chk_disputes_reason_len"),
        sa.CheckConstraint("category IN ('quality','no_show','overcharge','damage','other')", name="chk_disputes_category"),
        sa.CheckConstraint("status IN ('opened','under_review','auto_escalated','resolved')", name="chk_disputes_status"),
        sa.CheckConstraint("resolution IN ('refund_full','refund_partial','refund_denied')", name="chk_disputes_resolution"),
        sa.CheckConstraint("refund_percent >= 1 AND refund_percent <= 99", name="chk_disputes_refund_percent")
    )
    op.create_index("idx_disputes_unresolved", "disputes", ["status"], postgresql_where=sa.text("status != 'resolved'"))
    op.create_index("idx_disputes_response_deadline", "disputes", ["response_deadline"], postgresql_where=sa.text("status = 'opened'"))

def downgrade() -> None:
    op.drop_index("idx_disputes_response_deadline", table_name="disputes", postgresql_where=sa.text("status = 'opened'"))
    op.drop_index("idx_disputes_unresolved", table_name="disputes", postgresql_where=sa.text("status != 'resolved'"))
    op.drop_table("disputes")
