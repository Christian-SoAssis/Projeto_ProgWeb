"""contracts

Revision ID: 008
Revises: 007
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("requests.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("agreed_cents", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("payment_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payout_scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payout_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("agreed_cents > 0", name="chk_contracts_agreed_cents"),
        sa.CheckConstraint("status IN ('active','payment_confirmed','completed','disputed','refunded','partially_refunded','cancelled')", name="chk_contracts_status")
    )
    op.create_index("idx_contracts_prof_status", "contracts", ["professional_id", "status"])
    op.create_index("idx_contracts_client_status", "contracts", ["client_id", "status"])
    op.create_index("idx_contracts_payout_scheduled", "contracts", ["status", "payout_scheduled_at"], postgresql_where=sa.text("status = 'payment_confirmed'"))

def downgrade() -> None:
    op.drop_index("idx_contracts_payout_scheduled", table_name="contracts", postgresql_where=sa.text("status = 'payment_confirmed'"))
    op.drop_index("idx_contracts_client_status", table_name="contracts")
    op.drop_index("idx_contracts_prof_status", table_name="contracts")
    op.drop_table("contracts")
