"""add job view tracking

Revision ID: add_job_view_tracking
Revises: add_tagline_field
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_job_view_tracking'
down_revision = 'add_tagline_field'
branch_labels = None
depends_on = None


def upgrade():
    # Add view tracking columns to job table
    op.add_column('job', sa.Column('last_viewed', sa.DateTime, nullable=True))
    op.add_column('job', sa.Column('view_count', sa.Integer, server_default='0', nullable=False))


def downgrade():
    # Remove view tracking columns from job table
    op.drop_column('job', 'last_viewed')
    op.drop_column('job', 'view_count') 