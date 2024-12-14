"""add tagline field

Revision ID: add_tagline_field
Revises: initial_schema
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tagline_field'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add tagline column to locksmith table
    op.add_column('locksmith', sa.Column('tagline', sa.String(100), nullable=True))
    op.add_column('locksmith', sa.Column('years_experience', sa.Integer, nullable=True))
    op.add_column('locksmith', sa.Column('license_number', sa.String(50), nullable=True))
    op.add_column('locksmith', sa.Column('service_areas', sa.String(500), nullable=True))


def downgrade():
    # Remove tagline column from locksmith table
    op.drop_column('locksmith', 'tagline')
    op.drop_column('locksmith', 'years_experience')
    op.drop_column('locksmith', 'license_number')
    op.drop_column('locksmith', 'service_areas') 