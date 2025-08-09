"""
Unit tests for ApprovalGroup repository
"""
import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.models.approval_group import ApprovalGroup
from app.repositories.approval_group import approval_group_repository
from app.schemas.approval_group import ApprovalGroupCreate, ApprovalGroupUpdate


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestApprovalGroupRepository:
    """Test cases for ApprovalGroup repository"""
    
    @pytest_asyncio.fixture
    async def clean_approval_groups(self, db_session: AsyncSession):
        """Clean approval_groups table before each test"""
        await db_session.execute(delete(ApprovalGroup))
        await db_session.commit()
        yield
        await db_session.execute(delete(ApprovalGroup))
        await db_session.commit()
    
    async def test_create_approval_group(self, db_session: AsyncSession, clean_approval_groups):
        """Test creating a new approval group"""
        group_data = ApprovalGroupCreate(
            group_name="技術審査グループ",
            description="技術関連記事の審査を担当"
        )
        
        created_group = await approval_group_repository.create(db_session, obj_in=group_data)
        
        assert created_group.group_name == "技術審査グループ"
        assert created_group.description == "技術関連記事の審査を担当"
        assert isinstance(created_group.group_id, UUID)
        assert created_group.created_at is not None
        assert created_group.updated_at is not None
    
    async def test_get_by_id(self, db_session: AsyncSession, clean_approval_groups):
        """Test getting approval group by ID"""
        # Create test data
        group_data = ApprovalGroupCreate(
            group_name="テストグループ",
            description="テスト用"
        )
        created_group = await approval_group_repository.create(db_session, obj_in=group_data)
        
        # Test retrieval
        retrieved_group = await approval_group_repository.get_by_id(
            db_session, 
            group_id=created_group.group_id
        )
        
        assert retrieved_group is not None
        assert retrieved_group.group_id == created_group.group_id
        assert retrieved_group.group_name == "テストグループ"
        assert retrieved_group.description == "テスト用"
    
    async def test_get_by_id_not_found(self, db_session: AsyncSession, clean_approval_groups):
        """Test getting approval group by non-existent ID"""
        non_existent_id = uuid4()
        
        retrieved_group = await approval_group_repository.get_by_id(
            db_session, 
            group_id=non_existent_id
        )
        
        assert retrieved_group is None
    
    async def test_get_multi(self, db_session: AsyncSession, clean_approval_groups):
        """Test getting multiple approval groups"""
        # Create test data
        group_data_1 = ApprovalGroupCreate(
            group_name="グループ1",
            description="説明1"
        )
        group_data_2 = ApprovalGroupCreate(
            group_name="グループ2", 
            description="説明2"
        )
        
        await approval_group_repository.create(db_session, obj_in=group_data_1)
        await approval_group_repository.create(db_session, obj_in=group_data_2)
        
        # Test retrieval
        groups = await approval_group_repository.get_multi(db_session, skip=0, limit=10)
        
        assert len(groups) == 2
        group_names = [group.group_name for group in groups]
        assert "グループ1" in group_names
        assert "グループ2" in group_names
    
    async def test_update_approval_group(self, db_session: AsyncSession, clean_approval_groups):
        """Test updating approval group"""
        # Create test data
        group_data = ApprovalGroupCreate(
            group_name="元のグループ名",
            description="元の説明"
        )
        created_group = await approval_group_repository.create(db_session, obj_in=group_data)
        
        # Update data
        update_data = ApprovalGroupUpdate(
            group_name="更新されたグループ名",
            description="更新された説明"
        )
        
        updated_group = await approval_group_repository.update(
            db_session,
            db_obj=created_group,
            obj_in=update_data
        )
        
        assert updated_group.group_id == created_group.group_id
        assert updated_group.group_name == "更新されたグループ名"
        assert updated_group.description == "更新された説明"
        assert updated_group.updated_at >= created_group.updated_at
    
    async def test_delete_approval_group(self, db_session: AsyncSession, clean_approval_groups):
        """Test deleting approval group"""
        # Create test data
        group_data = ApprovalGroupCreate(
            group_name="削除対象グループ",
            description="削除テスト用"
        )
        created_group = await approval_group_repository.create(db_session, obj_in=group_data)
        group_id = created_group.group_id
        
        # Delete
        await approval_group_repository.remove(db_session, id=group_id)
        
        # Verify deletion
        retrieved_group = await approval_group_repository.get_by_id(db_session, group_id=group_id)
        assert retrieved_group is None
    
    async def test_get_by_name(self, db_session: AsyncSession, clean_approval_groups):
        """Test getting approval group by name"""
        # Create test data
        group_data = ApprovalGroupCreate(
            group_name="ユニークグループ名",
            description="名前で検索テスト用"
        )
        created_group = await approval_group_repository.create(db_session, obj_in=group_data)
        
        # Test retrieval by name
        retrieved_group = await approval_group_repository.get_by_name(
            db_session,
            group_name="ユニークグループ名"
        )
        
        assert retrieved_group is not None
        assert retrieved_group.group_id == created_group.group_id
        assert retrieved_group.group_name == "ユニークグループ名"
    
    async def test_get_by_name_not_found(self, db_session: AsyncSession, clean_approval_groups):
        """Test getting approval group by non-existent name"""
        retrieved_group = await approval_group_repository.get_by_name(
            db_session,
            group_name="存在しないグループ名"
        )
        
        assert retrieved_group is None