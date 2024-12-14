"""update missing application dates

Revision ID: update_missing_application_dates
Revises: add_location_details
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'update_missing_application_dates'
down_revision = 'add_location_details'
branch_labels = None
depends_on = None


def upgrade():
    # Get the database connection
    connection = op.get_bind()
    
    # Update locksmiths with missing application dates
    connection.execute(
        sa.text(
            "UPDATE locksmith SET application_date = created_at "
            "WHERE application_date IS NULL AND created_at IS NOT NULL"
        )
    )
    
    # For any remaining NULL application_dates, set to current time
    connection.execute(
        sa.text(
            "UPDATE locksmith SET application_date = :now "
            "WHERE application_date IS NULL"
        ),
        {"now": datetime.utcnow()}
    )


def downgrade():
    pass 