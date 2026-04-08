"""sync professionals table with current model

Revision ID: 018
Revises: 017
Create Date: 2026-04-08

Adiciona colunas faltantes (rejection_reason, search_vector) ao modelo atual.
NÃO remove colunas antigas para evitar perda de dados.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def _has_column(conn, table: str, column: str) -> bool:
    inspector = sa.inspect(conn)
    return column in [col['name'] for col in inspector.get_columns(table)]


def upgrade() -> None:
    conn = op.get_bind()

    # Adicionar colunas que o modelo SQLAlchemy espera mas que ainda não existem no banco
    if not _has_column(conn, 'professionals', 'rejection_reason'):
        op.add_column('professionals', sa.Column('rejection_reason', sa.String(500), nullable=True))

    if not _has_column(conn, 'professionals', 'search_vector'):
        op.add_column('professionals', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))

    # latitude e longitude podem já ter sido adicionadas por run anterior da migration
    if not _has_column(conn, 'professionals', 'latitude'):
        op.add_column('professionals', sa.Column('latitude', sa.Float(), nullable=True))

    if not _has_column(conn, 'professionals', 'longitude'):
        op.add_column('professionals', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()

    for col in ['rejection_reason', 'search_vector']:
        if _has_column(conn, 'professionals', col):
            op.drop_column('professionals', col)
