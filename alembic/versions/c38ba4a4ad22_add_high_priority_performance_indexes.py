"""add_high_priority_performance_indexes

Revision ID: c38ba4a4ad22
Revises: a39886d50779
Create Date: 2025-07-16 12:50:34.936568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c38ba4a4ad22'
down_revision: Union[str, None] = 'a39886d50779'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with high priority performance indexes."""
    # Add partial index for is_active (only true values)
    # This optimizes queries filtering for active users
    op.execute("""
        CREATE INDEX idx_users_is_active_true 
        ON users (is_active) 
        WHERE is_active = true
    """)
    
    # Add index for group column
    # This optimizes group-based user searches and statistics
    op.create_index(
        'idx_users_group', 
        'users', 
        ['group']
    )


def downgrade() -> None:
    """Downgrade schema by removing performance indexes."""
    # Remove indexes in reverse order
    op.drop_index('idx_users_group', table_name='users')
    op.execute("DROP INDEX IF EXISTS idx_users_is_active_true")