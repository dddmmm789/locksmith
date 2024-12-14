"""add location details

Revision ID: add_location_details
Revises: add_job_view_tracking
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_location_details'
down_revision = 'add_job_view_tracking'
branch_labels = None
depends_on = None


def upgrade():
    # Add location_details column to job table
    op.add_column('job', sa.Column('location_details', sa.Text, nullable=True))


def downgrade():
    # Remove location_details column from job table
    op.drop_column('job', 'location_details') 