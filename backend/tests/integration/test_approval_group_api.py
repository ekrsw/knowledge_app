"""
Integration tests for ApprovalGroup API endpoints
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.models.approval_group import ApprovalGroup
from app.repositories.approval_group import approval_group_repository
from app.schemas.approval_group import ApprovalGroupCreate


class TestApprovalGroupAPI:
    """Test cases for ApprovalGroup API endpoints"""
    
    @pytest.fixture
    async def clean_approval_groups(self, db_session: AsyncSession):
        """Clean approval_groups table before each test"""
        await db_session.execute(delete(ApprovalGroup))
        await db_session.commit()
        yield
        await db_session.execute(delete(ApprovalGroup))
        await db_session.commit()
    
    @pytest.fixture
    async def sample_approval_group(self, db_session: AsyncSession):
        """Create a sample approval group for testing"""
        group_data = ApprovalGroupCreate(
            group_name="サンプル審査グループ",
            description="APIテスト用のサンプルグループ"
        )
        return await approval_group_repository.create(db_session, obj_in=group_data)
    
    async def test_get_approval_groups(self, client: AsyncClient, clean_approval_groups, sample_approval_group):
        """Test GET /api/v1/approval-groups/"""
        response = await client.get("/api/v1/approval-groups/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["group_name"] == "サンプル審査グループ"
        assert data[0]["description"] == "APIテスト用のサンプルグループ"
        assert "group_id" in data[0]
        assert "created_at" in data[0]
        assert "updated_at" in data[0]
    
    async def test_get_approval_group_by_id(self, client: AsyncClient, clean_approval_groups, sample_approval_group):
        """Test GET /api/v1/approval-groups/{group_id}"""
        group_id = str(sample_approval_group.group_id)
        response = await client.get(f"/api/v1/approval-groups/{group_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group_id
        assert data["group_name"] == "サンプル審査グループ"
        assert data["description"] == "APIテスト用のサンプルグループ"
    
    async def test_get_approval_group_not_found(self, client: AsyncClient, clean_approval_groups):
        """Test GET /api/v1/approval-groups/{group_id} with non-existent ID"""
        non_existent_id = str(uuid4())
        response = await client.get(f"/api/v1/approval-groups/{non_existent_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Approval group not found"
    
    async def test_create_approval_group(self, client: AsyncClient, clean_approval_groups):
        """Test POST /api/v1/approval-groups/"""
        group_data = {
            "group_name": "新規審査グループ",
            "description": "新しく作成されたグループ"
        }
        
        response = await client.post("/api/v1/approval-groups/", json=group_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["group_name"] == "新規審査グループ"
        assert data["description"] == "新しく作成されたグループ"
        assert "group_id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_create_approval_group_validation_error(self, client: AsyncClient, clean_approval_groups):
        """Test POST /api/v1/approval-groups/ with validation errors"""
        # Empty group_name
        group_data = {
            "group_name": "",
            "description": "説明あり"
        }
        
        response = await client.post("/api/v1/approval-groups/", json=group_data)
        assert response.status_code == 422
        
        # Missing required field
        group_data = {
            "description": "group_nameなし"
        }
        
        response = await client.post("/api/v1/approval-groups/", json=group_data)
        assert response.status_code == 422
    
    async def test_update_approval_group(self, client: AsyncClient, clean_approval_groups, sample_approval_group):
        """Test PUT /api/v1/approval-groups/{group_id}"""
        group_id = str(sample_approval_group.group_id)
        update_data = {
            "group_name": "更新されたグループ名",
            "description": "更新された説明"
        }
        
        response = await client.put(f"/api/v1/approval-groups/{group_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group_id
        assert data["group_name"] == "更新されたグループ名"
        assert data["description"] == "更新された説明"
    
    async def test_update_approval_group_not_found(self, client: AsyncClient, clean_approval_groups):
        """Test PUT /api/v1/approval-groups/{group_id} with non-existent ID"""
        non_existent_id = str(uuid4())
        update_data = {
            "group_name": "更新されたグループ名",
            "description": "更新された説明"
        }
        
        response = await client.put(f"/api/v1/approval-groups/{non_existent_id}", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Approval group not found"
    
    async def test_update_approval_group_partial(self, client: AsyncClient, clean_approval_groups, sample_approval_group):
        """Test PUT /api/v1/approval-groups/{group_id} with partial update"""
        group_id = str(sample_approval_group.group_id)
        update_data = {
            "group_name": "部分更新されたグループ名"
            # description は更新しない
        }
        
        response = await client.put(f"/api/v1/approval-groups/{group_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group_id
        assert data["group_name"] == "部分更新されたグループ名"
        assert data["description"] == "APIテスト用のサンプルグループ"  # 元の値のまま
    
    async def test_get_approval_groups_with_pagination(self, client: AsyncClient, clean_approval_groups, db_session: AsyncSession):
        """Test GET /api/v1/approval-groups/ with pagination"""
        # Create multiple approval groups
        for i in range(5):
            group_data = ApprovalGroupCreate(
                group_name=f"グループ{i+1}",
                description=f"説明{i+1}"
            )
            await approval_group_repository.create(db_session, obj_in=group_data)
        
        # Test pagination
        response = await client.get("/api/v1/approval-groups/?skip=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    
    async def test_approval_group_uuid_validation(self, client: AsyncClient, clean_approval_groups):
        """Test UUID validation for group_id parameter"""
        invalid_uuid = "invalid-uuid-format"
        response = await client.get(f"/api/v1/approval-groups/{invalid_uuid}")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data