"""add payments and category fee_percentage

Revision ID: 019
Revises: 018
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add fee_percentage to categories
    op.add_column('categories', sa.Column('fee_percentage', sa.Integer(), nullable=False, server_default='10'))

    # 2. Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('contract_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contracts.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('fee_cents', sa.Integer(), nullable=False),
        sa.Column('professional_amount_cents', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pending'),
        sa.Column('mp_preference_id', sa.String(length=100), nullable=True),
        sa.Column('mp_payment_id', sa.String(length=100), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    # 3. Add payment_id to disputes (if the table exists)
    # The previous migration 012 already created 'disputes'
    op.add_column('disputes', sa.Column('payment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payments.id', ondelete='RESTRICT'), nullable=True))

def downgrade() -> None:
    op.drop_column('disputes', 'payment_id')
    op.drop_table('payments')
    op.drop_column('categories', 'fee_percentage')
