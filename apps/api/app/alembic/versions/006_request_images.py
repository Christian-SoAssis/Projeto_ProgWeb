"""request_images

Revision ID: 006
Revises: 005
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "request_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("analyzed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("content_type IN ('image/jpeg','image/png','image/webp')", name="chk_req_img_content_type"),
        sa.CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="chk_req_img_size")
    )
    op.create_index("idx_req_img_request_id", "request_images", ["request_id"])
    op.create_index("idx_req_img_analyzed", "request_images", ["analyzed"], postgresql_where=sa.text("analyzed = false"))

def downgrade() -> None:
    op.drop_index("idx_req_img_analyzed", table_name="request_images", postgresql_where=sa.text("analyzed = false"))
    op.drop_index("idx_req_img_request_id", table_name="request_images")
    op.drop_table("request_images")
