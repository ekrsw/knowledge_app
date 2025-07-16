"""add_composite_active_created_index

Revision ID: 39d20b6292b8
Revises: 6146eadb36bb
Create Date: 2025-07-16 12:57:34.353723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39d20b6292b8'
down_revision: Union[str, None] = '6146eadb36bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with composite (is_active, created_at) index."""
    # Add composite partial index for active users with time series
    # This optimizes queries for active users ordered by creation time
    op.execute("""
        CREATE INDEX idx_users_active_created_desc 
        ON users (is_active, created_at DESC) 
        WHERE is_active = true
    """)


def downgrade() -> None:
    """Downgrade schema by removing composite index."""
    op.execute("DROP INDEX IF EXISTS idx_users_active_created_desc")