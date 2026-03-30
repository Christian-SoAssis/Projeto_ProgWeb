"""reviews

Revision ID: 009
Revises: 008
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("score_punctuality", sa.Float(), nullable=True),
        sa.Column("score_quality", sa.Float(), nullable=True),
        sa.Column("score_cleanliness", sa.Float(), nullable=True),
        sa.Column("score_communication", sa.Float(), nullable=True),
        sa.Column("is_authentic", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="chk_reviews_rating"),
        sa.CheckConstraint("length(text) >= 10", name="chk_reviews_text_len"),
        sa.CheckConstraint("score_punctuality >= 0 AND score_punctuality <= 1", name="chk_reviews_score_punctuality"),
        sa.CheckConstraint("score_quality >= 0 AND score_quality <= 1", name="chk_reviews_score_quality"),
        sa.CheckConstraint("score_cleanliness >= 0 AND score_cleanliness <= 1", name="chk_reviews_score_cleanliness"),
        sa.CheckConstraint("score_communication >= 0 AND score_communication <= 1", name="chk_reviews_score_communication")
    )
    op.create_index("idx_reviews_reviewee_authentic", "reviews", ["reviewee_id", "is_authentic"], postgresql_where=sa.text("is_authentic = true"))
    op.create_index("idx_reviews_reviewer_created", "reviews", ["reviewer_id", sa.text("created_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_reviews_reviewer_created", table_name="reviews")
    op.drop_index("idx_reviews_reviewee_authentic", table_name="reviews", postgresql_where=sa.text("is_authentic = true"))
    op.drop_table("reviews")
