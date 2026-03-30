"""requests

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column("urgency", sa.Text(), nullable=False),
        sa.Column("budget_cents", sa.Integer(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="open"),
        sa.Column("ai_complexity", sa.Text(), nullable=True),
        sa.Column("ai_urgency", sa.Text(), nullable=True),
        sa.Column("ai_specialties", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("length(title) >= 5", name="chk_req_title_len"),
        sa.CheckConstraint("urgency IN ('immediate','scheduled','flexible')", name="chk_req_urgency"),
        sa.CheckConstraint("budget_cents > 0", name="chk_req_budget"),
        sa.CheckConstraint("status IN ('open','matched','in_progress','done','cancelled')", name="chk_req_status"),
        sa.CheckConstraint("ai_complexity IN ('simple','medium','complex')", name="chk_req_ai_complex"),
        sa.CheckConstraint("ai_urgency IN ('low','medium','high')", name="chk_req_ai_urgency")
    )
    
    op.create_index("idx_requests_status_cat", "requests", ["status", "category_id"])
    op.create_index("idx_requests_client_created", "requests", ["client_id", sa.text("created_at DESC")])
    op.create_index("idx_requests_location", "requests", ["location"], postgresql_using="gist")

def downgrade() -> None:
    op.drop_index("idx_requests_location", table_name="requests", postgresql_using="gist")
    op.drop_index("idx_requests_client_created", table_name="requests")
    op.drop_index("idx_requests_status_cat", table_name="requests")
    op.drop_table("requests")
