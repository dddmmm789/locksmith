"""add terms acceptance

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-12-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('locksmith', sa.Column('terms_accepted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('locksmith', sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('locksmith', 'terms_accepted_at')
    op.drop_column('locksmith', 'terms_accepted')
