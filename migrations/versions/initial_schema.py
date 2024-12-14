"""initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create admin table
    op.create_table('admin',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), nullable=False),
        sa.Column('password_hash', sa.String(128)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    # Create locksmith table with minimal fields for OTP
    op.create_table('locksmith',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100)),  # Not required during OTP
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('email', sa.String(120), unique=True),  # Not required during OTP
        sa.Column('profile_photo', sa.String(255)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('phone_verified', sa.Boolean, default=False),
        sa.Column('otp_code', sa.String(6)),
        sa.Column('otp_expires_at', sa.DateTime),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('application_date', sa.DateTime),
        sa.Column('application_notes', sa.Text),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Column('reviewed_by', sa.Integer, sa.ForeignKey('admin.id')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_number')
    )

    # Create job table
    op.create_table('job',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tracking_id', sa.String(36), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('customer_address', sa.String(200), nullable=False),
        sa.Column('location_details', sa.Text),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('locksmith_id', sa.Integer, sa.ForeignKey('locksmith.id')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tracking_id')
    )

    # Create review table
    op.create_table('review',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('locksmith_id', sa.Integer, sa.ForeignKey('locksmith.id')),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('comment', sa.Text),
        sa.Column('reviewer_name', sa.String(100)),
        sa.Column('review_date', sa.DateTime, server_default=sa.func.now()),
        sa.Column('verified', sa.Boolean, server_default='0'),
        sa.Column('job_type', sa.String(50)),
        sa.Column('location', sa.String(100)),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('review')
    op.drop_table('job')
    op.drop_table('locksmith')
    op.drop_table('admin') 