"""consent_logs

Revision ID: 014
Revises: 013
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "consent_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("consent_type", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("ip_address", postgresql.INET(), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("consent_type IN ('terms','privacy','marketing')", name="chk_consent_logs_type")
    )
    op.create_index("idx_consent_logs_user_type_date", "consent_logs", ["user_id", "consent_type", sa.text("accepted_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_consent_logs_user_type_date", table_name="consent_logs")
    op.drop_table("consent_logs")
