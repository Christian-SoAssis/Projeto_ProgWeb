"""push_subscriptions

Revision ID: 015
Revises: 014
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "push_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False, unique=True),
        sa.Column("key_p256dh", sa.Text(), nullable=False),
        sa.Column("key_auth", sa.Text(), nullable=False),
        sa.Column("device_label", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index("idx_push_subs_user_active", "push_subscriptions", ["user_id"], postgresql_where=sa.text("is_active = true"))

def downgrade() -> None:
    op.drop_index("idx_push_subs_user_active", table_name="push_subscriptions", postgresql_where=sa.text("is_active = true"))
    op.drop_table("push_subscriptions")
