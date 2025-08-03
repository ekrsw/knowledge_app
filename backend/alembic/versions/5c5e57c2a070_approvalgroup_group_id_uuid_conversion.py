"""ApprovalGroup group_id UUID conversion

Revision ID: 5c5e57c2a070
Revises: c228a4e4e4f6
Create Date: 2025-08-04 01:26:06.419451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c5e57c2a070'
down_revision = 'c228a4e4e4f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ApprovalGroup group_id を UUID に変換
    外部キー制約を適切に処理するため、以下の順序で実行：
    1. 外部キー制約削除
    2. 主キー型変換
    3. 外部キー型変換
    4. 外部キー制約再作成
    """
    
    # Step 1: Drop foreign key constraints that reference approval_groups.group_id
    op.drop_constraint('articles_approval_group_fkey', 'articles', type_='foreignkey')
    op.drop_constraint('users_approval_group_id_fkey', 'users', type_='foreignkey')
    
    # Step 2: Convert approval_groups.group_id to UUID (primary key)
    op.execute("ALTER TABLE approval_groups ALTER COLUMN group_id TYPE UUID USING gen_random_uuid()")
    
    # Step 3: Convert referencing columns to UUID
    op.execute("ALTER TABLE articles ALTER COLUMN approval_group TYPE UUID USING NULL::UUID")
    op.execute("ALTER TABLE users ALTER COLUMN approval_group_id TYPE UUID USING NULL::UUID")
    
    # Step 4: Re-add foreign key constraints
    op.create_foreign_key(
        'articles_approval_group_fkey',
        'articles', 
        'approval_groups',
        ['approval_group'], 
        ['group_id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'users_approval_group_id_fkey',
        'users',
        'approval_groups', 
        ['approval_group_id'],
        ['group_id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """
    緊急時のロールバック用（データ損失の可能性あり）
    UUID から VARCHAR への変換は情報損失を伴うため、緊急時のみ使用
    """
    # 逆順で実行
    op.drop_constraint('users_approval_group_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('articles_approval_group_fkey', 'articles', type_='foreignkey')
    
    op.execute("ALTER TABLE users ALTER COLUMN approval_group_id TYPE VARCHAR(50) USING NULL")
    op.execute("ALTER TABLE articles ALTER COLUMN approval_group TYPE VARCHAR(50) USING NULL")
    op.execute("ALTER TABLE approval_groups ALTER COLUMN group_id TYPE VARCHAR(50) USING ''")
    
    op.create_foreign_key('articles_approval_group_fkey', 'articles', 'approval_groups', ['approval_group'], ['group_id'], ondelete='SET NULL')
    op.create_foreign_key('users_approval_group_id_fkey', 'users', 'approval_groups', ['approval_group_id'], ['group_id'], ondelete='SET NULL')