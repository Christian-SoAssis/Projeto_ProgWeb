"""add professional pix and availability

Revision ID: ae8089c9422c
Revises: 019
Create Date: 2026-06-02 21:21:41.099679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ae8089c9422c'
down_revision: Union[str, None] = '019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create professional_availabilities table
    op.create_table('professional_availabilities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('professional_id', sa.UUID(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('professional_id', 'day_of_week', name='uq_professional_day_availability')
    )
    
    # 2. Create professional_pix_keys table
    op.create_table('professional_pix_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('professional_id', sa.UUID(), nullable=False),
        sa.Column('key_type', sa.String(length=20), nullable=False),
        sa.Column('key_value', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['professional_id'], ['professionals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('professional_id')
    )

    # 3. Add columns to contracts table
    op.add_column('contracts', sa.Column('scheduled_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('contracts', sa.Column('scheduled_end', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('contracts', 'scheduled_end')
    op.drop_column('contracts', 'scheduled_start')
    op.drop_table('professional_pix_keys')
    op.drop_table('professional_availabilities')
