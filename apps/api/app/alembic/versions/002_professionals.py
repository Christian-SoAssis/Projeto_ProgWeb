"""professionals

Revision ID: 002
Revises: 001
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
import geoalchemy2
import pgvector.sqlalchemy

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "professionals",
        sa.Column("id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("location", geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column("service_radius_km", sa.Float(), nullable=False, server_default="20.0"),
        sa.Column("avg_response_min", sa.Integer(), nullable=True),
        sa.Column("completed_jobs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reputation_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("cancel_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("hourly_rate_cents", sa.Integer(), nullable=True),
        sa.Column("profile_embedding", pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("reputation_score >= 0 AND reputation_score <= 5", name="chk_prof_reputation"),
        sa.CheckConstraint("cancel_rate >= 0 AND cancel_rate <= 1", name="chk_prof_cancel_rate"),
        sa.CheckConstraint("hourly_rate_cents > 0", name="chk_prof_hourly_rate")
    )
    
    op.create_index("idx_professionals_location", "professionals", ["location"], postgresql_using="gist")
    op.create_index(
        "idx_professionals_profile_embedding", 
        "professionals", 
        ["profile_embedding"], 
        postgresql_using="ivfflat", 
        postgresql_with={"lists": 100},
        postgresql_ops={"profile_embedding": "vector_cosine_ops"}
    )
    op.create_index("idx_professionals_is_verified", "professionals", ["is_verified"], postgresql_where=sa.text("is_verified = true"))
    op.create_index("idx_professionals_reputation_desc", "professionals", [sa.text("reputation_score DESC")])

def downgrade() -> None:
    op.drop_index("idx_professionals_reputation_desc", table_name="professionals")
    op.drop_index("idx_professionals_is_verified", table_name="professionals", postgresql_where=sa.text("is_verified = true"))
    op.drop_index("idx_professionals_profile_embedding", table_name="professionals", postgresql_using="ivfflat", postgresql_with={"lists": 100})
    op.drop_index("idx_professionals_location", table_name="professionals", postgresql_using="gist")
    op.drop_table("professionals")
