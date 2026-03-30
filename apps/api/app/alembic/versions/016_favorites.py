"""favorites

Revision ID: 016
Revises: 015
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("client_id", "professional_id", name="uq_favorites_client_prof")
    )
    op.create_index("idx_favorites_client_created", "favorites", ["client_id", sa.text("created_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_favorites_client_created", table_name="favorites")
    op.drop_table("favorites")
