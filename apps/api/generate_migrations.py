import os

TARGET_DIR = "app/alembic/versions"

MIGRATIONS = {
    "002_professionals.py": """\"\"\"professionals

Revision ID: 002
Revises: 001
\"\"\"
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
""",
    "003_categories.py": """\"\"\"categories

Revision ID: 003
Revises: 002
\"\"\"
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#1a9878"),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )

    op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_index("ix_categories_parent", "categories", ["parent_id"])

    # Constraint: validar formato hex da cor (#RRGGBB)
    op.create_check_constraint(
        "chk_categories_color_format",
        "categories",
        "color ~ '^#[0-9a-fA-F]{6}$'",
    )


def downgrade() -> None:
    op.drop_constraint("chk_categories_color_format", "categories", type_="check")
    op.drop_index("ix_categories_parent", table_name="categories")
    op.drop_index("ix_categories_slug", table_name="categories")
    op.drop_table("categories")
""",
    "004_professional_categories.py": """\"\"\"professional_categories

Revision ID: 004
Revises: 003
\"\"\"
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "professional_categories",
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.CheckConstraint("years_experience >= 0", name="chk_prof_cat_experience")
    )
    op.create_index("idx_prof_cat_category_id", "professional_categories", ["category_id"])

def downgrade() -> None:
    op.drop_index("idx_prof_cat_category_id", table_name="professional_categories")
    op.drop_table("professional_categories")
""",
    "005_requests.py": """\"\"\"requests

Revision ID: 005
Revises: 004
\"\"\"
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
""",
    "006_request_images.py": """\"\"\"request_images

Revision ID: 006
Revises: 005
\"\"\"
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
""",
    "007_bids.py": """\"\"\"bids

Revision ID: 007
Revises: 006
\"\"\"
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "bids",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("professional_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("professionals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("estimated_hours", sa.Integer(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("request_id", "professional_id", name="uq_bids_request_professional"),
        sa.CheckConstraint("price_cents > 0", name="chk_bids_price"),
        sa.CheckConstraint("estimated_hours > 0", name="chk_bids_est_hours"),
        sa.CheckConstraint("status IN ('pending','accepted','rejected','cancelled')", name="chk_bids_status")
    )
    op.create_index("idx_bids_request_status", "bids", ["request_id", "status"])
    op.create_index("idx_bids_prof_created", "bids", ["professional_id", sa.text("created_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_bids_prof_created", table_name="bids")
    op.drop_index("idx_bids_request_status", table_name="bids")
    op.drop_table("bids")
""",
    "008_contracts.py": """\"\"\"contracts

Revision ID: 008
Revises: 007
\"\"\"
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
""",
    "009_reviews.py": """\"\"\"reviews

Revision ID: 009
Revises: 008
\"\"\"
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
""",
    "010_messages.py": """\"\"\"messages

Revision ID: 010
Revises: 009
\"\"\"
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("length(content) >= 1", name="chk_messages_content_len")
    )
    op.create_index("idx_messages_contract_created", "messages", ["contract_id", sa.text("created_at DESC")])

def downgrade() -> None:
    op.drop_index("idx_messages_contract_created", table_name="messages")
    op.drop_table("messages")
""",
    "011_notifications.py": """\"\"\"notifications

Revision ID: 011
Revises: 010
\"\"\"
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
""",
    "012_disputes.py": """\"\"\"disputes

Revision ID: 012
Revises: 011
\"\"\"
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
""",
    "013_commission_rates.py": """\"\"\"commission_rates

Revision ID: 013
Revises: 012
\"\"\"
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "commission_rates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="CASCADE"), nullable=True),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("effective_until", sa.Date(), nullable=True),
        sa.CheckConstraint("percent > 0 AND percent < 100", name="chk_comm_rates_percent"),
        sa.CheckConstraint("effective_until IS NULL OR effective_until > effective_from", name="chk_comm_rates_dates")
    )
    op.create_index("idx_comm_rates_cat_effective", "commission_rates", ["category_id", sa.text("effective_from DESC")])
    
    # Inline seed
    op.execute("INSERT INTO commission_rates (id, category_id, percent) VALUES (gen_random_uuid(), NULL, 5.00)")

def downgrade() -> None:
    op.execute("DELETE FROM commission_rates WHERE category_id IS NULL")
    op.drop_index("idx_comm_rates_cat_effective", table_name="commission_rates")
    op.drop_table("commission_rates")
""",
    "014_consent_logs.py": """\"\"\"consent_logs

Revision ID: 014
Revises: 013
\"\"\"
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
""",
    "015_push_subscriptions.py": """\"\"\"push_subscriptions

Revision ID: 015
Revises: 014
\"\"\"
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
""",
    "016_favorites.py": """\"\"\"favorites

Revision ID: 016
Revises: 015
\"\"\"
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
"""
}

def main():
    for filename, content in MIGRATIONS.items():
        filepath = os.path.join(TARGET_DIR, filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created/Updated {filepath}")

if __name__ == "__main__":
    main()
