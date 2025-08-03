"""Model changes: UUID conversion and field removal

Revision ID: c228a4e4e4f6
Revises: e70510a1099e
Create Date: 2025-08-04 00:41:47.383094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c228a4e4e4f6'
down_revision = 'e70510a1099e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Model changes for UUID conversion and field removal.
    Since all tables are empty, we can safely drop and recreate constraints.
    """
    
    # Step 1: Drop all foreign key constraints that reference info_categories.category_id
    op.drop_constraint('articles_info_category_fkey', 'articles', type_='foreignkey')
    op.drop_constraint('revisions_after_info_category_fkey', 'revisions', type_='foreignkey')
    
    # Step 2: Remove article_pk fields first
    op.drop_index('ix_articles_article_pk', table_name='articles')
    op.drop_column('articles', 'article_pk')
    op.drop_column('revisions', 'target_article_pk')
    
    # Step 3: Convert info_categories.category_id to UUID (primary key)
    op.execute("ALTER TABLE info_categories ALTER COLUMN category_id TYPE UUID USING gen_random_uuid()")
    
    # Step 4: Convert referencing columns to UUID
    op.execute("ALTER TABLE articles ALTER COLUMN info_category TYPE UUID USING NULL::UUID")
    op.execute("ALTER TABLE revisions ALTER COLUMN after_info_category TYPE UUID USING NULL::UUID")
    
    # Step 5: Re-add foreign key constraints
    op.create_foreign_key(
        'articles_info_category_fkey', 
        'articles', 
        'info_categories', 
        ['info_category'], 
        ['category_id'], 
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'revisions_after_info_category_fkey', 
        'revisions', 
        'info_categories', 
        ['after_info_category'], 
        ['category_id'], 
        ondelete='SET NULL'
    )
    
    # Step 6: Update other columns (timestamp changes)
    op.alter_column('approval_groups', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('approval_groups', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    
    op.alter_column('articles', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('articles', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    
    op.alter_column('info_categories', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('info_categories', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    
    op.alter_column('revisions', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('revisions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    
    # Step 7: Update indexes
    op.drop_index('ix_revisions_created_at', table_name='revisions')
    op.create_index('idx_revision_created_at', 'revisions', ['created_at'], unique=False)
    
    # Step 8: Add updated_at column to simple_notifications and update indexes
    op.add_column('simple_notifications', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))
    op.alter_column('simple_notifications', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.drop_index('ix_simple_notifications_created_at', table_name='simple_notifications')
    op.create_index('idx_notification_created_at', 'simple_notifications', ['created_at'], unique=False)
    
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))


def downgrade() -> None:
    """
    Reverse the changes made in upgrade().
    Note: This is for emergency rollback only as data may be lost.
    """
    # Reverse the changes (simplified for emergency rollback)
    op.alter_column('users', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    
    op.drop_index('idx_notification_created_at', table_name='simple_notifications')
    op.create_index('ix_simple_notifications_created_at', 'simple_notifications', ['created_at'], unique=False)
    op.alter_column('simple_notifications', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.drop_column('simple_notifications', 'updated_at')
    
    op.drop_index('idx_revision_created_at', table_name='revisions')
    op.create_index('ix_revisions_created_at', 'revisions', ['created_at'], unique=False)
    
    # Add back removed columns
    op.add_column('revisions', sa.Column('target_article_pk', sa.VARCHAR(length=200), autoincrement=False, nullable=False, server_default=''))
    op.add_column('articles', sa.Column('article_pk', sa.VARCHAR(length=200), autoincrement=False, nullable=False, server_default=''))
    op.create_index('ix_articles_article_pk', 'articles', ['article_pk'], unique=False)
    
    # Note: Converting back from UUID to VARCHAR would lose data, 
    # so this downgrade is primarily for schema structure only
    op.drop_constraint('revisions_after_info_category_fkey', 'revisions', type_='foreignkey')
    op.drop_constraint('articles_info_category_fkey', 'articles', type_='foreignkey')
    
    op.execute("ALTER TABLE revisions ALTER COLUMN after_info_category TYPE VARCHAR(50) USING NULL")
    op.execute("ALTER TABLE articles ALTER COLUMN info_category TYPE VARCHAR(50) USING NULL")
    op.execute("ALTER TABLE info_categories ALTER COLUMN category_id TYPE VARCHAR(50) USING ''")
    
    op.create_foreign_key('articles_info_category_fkey', 'articles', 'info_categories', ['info_category'], ['category_id'], ondelete='SET NULL')
    op.create_foreign_key('revisions_after_info_category_fkey', 'revisions', 'info_categories', ['after_info_category'], ['category_id'], ondelete='SET NULL')