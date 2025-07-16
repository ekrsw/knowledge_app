"""add_created_at_desc_index

Revision ID: 6146eadb36bb
Revises: c38ba4a4ad22
Create Date: 2025-07-16 12:56:28.925141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6146eadb36bb'
down_revision: Union[str, None] = 'c38ba4a4ad22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with created_at descending index."""
    # Add descending index for created_at column
    # This optimizes time-series queries and getting latest users
    op.execute("""
        CREATE INDEX idx_users_created_at_desc 
        ON users (created_at DESC)
    """)


def downgrade() -> None:
    """Downgrade schema by removing created_at index."""
    op.execute("DROP INDEX IF EXISTS idx_users_created_at_desc")