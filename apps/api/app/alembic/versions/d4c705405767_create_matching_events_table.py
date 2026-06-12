"""create matching events table

Revision ID: d4c705405767
Revises: ae8089c9422c
Create Date: 2026-06-12 17:18:18.984748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4c705405767'
down_revision: Union[str, None] = 'ae8089c9422c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'matching_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bid_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['request_id'], ['requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bid_id'], ['bids.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_matching_events_request_id', 'matching_events', ['request_id'])
    op.create_index('ix_matching_events_professional_id', 'matching_events', ['professional_id'])


def downgrade() -> None:
    op.drop_index('ix_matching_events_professional_id', table_name='matching_events')
    op.drop_index('ix_matching_events_request_id', table_name='matching_events')
    op.drop_table('matching_events')

