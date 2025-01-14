"""existing schema

Revision ID: 120f6c7974a2
Revises: 
Create Date: 2024-12-15 20:03:27.896511

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '120f6c7974a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin')
    op.drop_table('job')
    op.drop_table('locksmith')
    op.drop_table('review')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('review',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('locksmith_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('reviewer_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('review_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('job_type', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('location', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['locksmith_id'], ['locksmith.id'], name='review_locksmith_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='review_pkey')
    )
    op.create_table('locksmith',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('locksmith_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('phone_number', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('profile_photo', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('phone_verified', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('otp_code', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
    sa.Column('otp_expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('application_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('application_notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('reviewed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('reviewed_by', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('tagline', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('years_experience', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('license_number', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('service_areas', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['reviewed_by'], ['admin.id'], name='locksmith_reviewed_by_fkey'),
    sa.PrimaryKeyConstraint('id', name='locksmith_pkey'),
    sa.UniqueConstraint('email', name='locksmith_email_key'),
    sa.UniqueConstraint('phone_number', name='locksmith_phone_number_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('job',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tracking_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('customer_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('customer_address', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('completed_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('locksmith_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('last_viewed', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('view_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('location_details', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['locksmith_id'], ['locksmith.id'], name='job_locksmith_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='job_pkey'),
    sa.UniqueConstraint('tracking_id', name='job_tracking_id_key')
    )
    op.create_table('admin',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='admin_pkey'),
    sa.UniqueConstraint('username', name='admin_username_key')
    )
    # ### end Alembic commands ###
