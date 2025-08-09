"""
Approval Group Management API Integration Tests

Tests for /api/v1/approval-groups endpoints including CRUD operations
and data validation.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from uuid import uuid4

from app.models.approval_group import ApprovalGroup
from tests.factories.approval_group_factory import ApprovalGroupFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def clean_approval_groups(db_session: AsyncSession):
    """Clean approval_groups table before each test"""
    await db_session.execute(delete(ApprovalGroup))
    await db_session.commit()
    yield
    await db_session.execute(delete(ApprovalGroup))
    await db_session.commit()


class TestApprovalGroupList:
    """Test approval group list endpoint (GET /api/v1/approval-groups/)"""
    
    async def test_list_approval_groups_empty(self, client: AsyncClient, db_session: AsyncSession, clean_approval_groups):
        """Test listing approval groups when none exist"""
        response = await client.get("/api/v1/approval-groups/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_list_approval_groups_with_data(self, client: AsyncClient, db_session: AsyncSession, clean_approval_groups):
        """Test listing approval groups with existing data"""
        # Create test approval groups
        group1 = await ApprovalGroupFactory.create_development_group(db_session)
        group2 = await ApprovalGroupFactory.create_quality_group(db_session)
        group3 = await ApprovalGroupFactory.create_management_group(db_session)
        
        response = await client.get("/api/v1/approval-groups/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify group data structure
        group_names = [group["group_name"] for group in data]
        assert "Development Team" in group_names
        assert "Quality Assurance" in group_names
        assert "Management Team" in group_names
        
        # Verify data structure
        for group in data:
            assert "group_id" in group
            assert "group_name" in group
            assert "description" in group
            assert "is_active" in group
            assert "created_at" in group
            assert "updated_at" in group
    
    async def test_list_approval_groups_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test pagination in approval group list"""
        # Get initial count
        initial_response = await client.get("/api/v1/approval-groups/")
        initial_count = len(initial_response.json())
        
        # Create multiple approval groups
        for i in range(5):
            await ApprovalGroupFactory.create(
                db_session,
                group_name=f"TestGroup{i}",
                description=f"Test group {i}"
            )
        
        # Get total count after adding
        total_response = await client.get("/api/v1/approval-groups/")
        total_count = len(total_response.json())
        assert total_count == initial_count + 5
        
        # Test with limit
        response = await client.get("/api/v1/approval-groups/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == min(3, total_count)  # Should get min(limit, total)
        
        # Test with skip
        skip_count = 2
        response = await client.get(f"/api/v1/approval-groups/?skip={skip_count}&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have total_count minus the skipped ones, limited by the limit parameter
        expected_count = max(0, min(10, total_count - skip_count))
        assert len(data) == expected_count


class TestApprovalGroupGet:
    """Test approval group retrieval endpoint (GET /api/v1/approval-groups/{group_id})"""
    
    async def test_get_approval_group_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting approval group by valid ID"""
        # Create a test approval group
        test_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        response = await client.get(f"/api/v1/approval-groups/{test_group.group_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["group_id"] == str(test_group.group_id)
        assert data["group_name"] == test_group.group_name
        assert data["description"] == test_group.description
        assert data["is_active"] == test_group.is_active
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_get_nonexistent_approval_group(self, client: AsyncClient):
        """Test getting non-existent approval group returns 404"""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/approval-groups/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_get_approval_group_invalid_uuid(self, client: AsyncClient):
        """Test getting approval group with invalid UUID format"""
        invalid_id = "not-a-uuid"
        response = await client.get(f"/api/v1/approval-groups/{invalid_id}")
        
        assert response.status_code == 422  # Validation error


class TestApprovalGroupCreate:
    """Test approval group creation endpoint (POST /api/v1/approval-groups/)"""
    
    async def test_create_approval_group_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful approval group creation"""
        group_data = {
            "group_name": "New Test Group",
            "description": "A new test approval group",
            "is_active": True
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        assert response.status_code == 201
        created_group = response.json()
        
        assert created_group["group_name"] == "New Test Group"
        assert created_group["description"] == "A new test approval group"
        assert created_group["is_active"] == True
        assert "group_id" in created_group
        assert "created_at" in created_group
        assert "updated_at" in created_group
    
    async def test_create_approval_group_minimal_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating approval group with minimal required data"""
        group_data = {
            "group_name": "Minimal Group"
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        assert response.status_code == 201
        created_group = response.json()
        
        assert created_group["group_name"] == "Minimal Group"
        assert created_group["description"] is None
        assert created_group["is_active"] == True  # Default value
    
    async def test_create_approval_group_missing_required_fields(self, client: AsyncClient):
        """Test creating approval group with missing required fields"""
        # Missing group_name
        response = await client.post(
            "/api/v1/approval-groups/",
            json={"description": "Group without name"}
        )
        assert response.status_code == 422
        
        # Empty data
        response = await client.post(
            "/api/v1/approval-groups/",
            json={}
        )
        assert response.status_code == 422
    
    async def test_create_approval_group_invalid_data_types(self, client: AsyncClient):
        """Test creating approval group with invalid data types"""
        # is_active should be boolean
        group_data = {
            "group_name": "Test Group",
            "is_active": "not-a-boolean"
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        assert response.status_code == 422
    
    async def test_create_approval_group_long_strings(self, client: AsyncClient):
        """Test creating approval group with very long strings"""
        group_data = {
            "group_name": "A" * 300,  # Very long name
            "description": "B" * 1000  # Very long description
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        # Should either succeed or fail gracefully with validation error
        assert response.status_code in [201, 422]


class TestApprovalGroupUpdate:
    """Test approval group update endpoint (PUT /api/v1/approval-groups/{group_id})"""
    
    async def test_update_approval_group_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful approval group update"""
        # Create a test approval group
        test_group = await ApprovalGroupFactory.create(
            db_session,
            group_name="Original Name",
            description="Original description",
            is_active=True
        )
        
        update_data = {
            "group_name": "Updated Name",
            "description": "Updated description",
            "is_active": False
        }
        
        response = await client.put(
            f"/api/v1/approval-groups/{test_group.group_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        
        assert updated["group_name"] == "Updated Name"
        assert updated["description"] == "Updated description"
        assert updated["is_active"] == False
        assert updated["group_id"] == str(test_group.group_id)
    
    async def test_update_approval_group_partial(self, client: AsyncClient, db_session: AsyncSession):
        """Test partial update of approval group"""
        # Create a test approval group
        test_group = await ApprovalGroupFactory.create(
            db_session,
            group_name="Original Name",
            description="Original description",
            is_active=True
        )
        
        # Update only one field
        update_data = {
            "group_name": "Partially Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/approval-groups/{test_group.group_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        
        assert updated["group_name"] == "Partially Updated Name"
        assert updated["description"] == "Original description"  # Unchanged
        assert updated["is_active"] == True  # Unchanged
    
    async def test_update_nonexistent_approval_group(self, client: AsyncClient):
        """Test updating non-existent approval group returns 404"""
        fake_id = str(uuid4())
        update_data = {
            "group_name": "Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/approval-groups/{fake_id}",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_approval_group_invalid_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating approval group with invalid data"""
        # Create a test approval group
        test_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # Invalid data types
        update_data = {
            "is_active": "not-a-boolean"
        }
        
        response = await client.put(
            f"/api/v1/approval-groups/{test_group.group_id}",
            json=update_data
        )
        
        assert response.status_code == 422
    
    async def test_update_approval_group_empty_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating approval group with empty data"""
        # Create a test approval group
        test_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # Empty update should succeed (no changes)
        response = await client.put(
            f"/api/v1/approval-groups/{test_group.group_id}",
            json={}
        )
        
        assert response.status_code == 200
        updated = response.json()
        
        # Should remain unchanged
        assert updated["group_name"] == test_group.group_name
        assert updated["description"] == test_group.description
        assert updated["is_active"] == test_group.is_active


class TestApprovalGroupEdgeCases:
    """Test edge cases and error handling"""
    
    async def test_approval_group_with_special_characters(self, client: AsyncClient):
        """Test approval group with special characters in name"""
        group_data = {
            "group_name": "Test-Group_123 (Special Characters!)",
            "description": "Group with special chars: @#$%^&*()"
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        assert response.status_code == 201
        created_group = response.json()
        assert created_group["group_name"] == group_data["group_name"]
        assert created_group["description"] == group_data["description"]
    
    async def test_approval_group_unicode_support(self, client: AsyncClient):
        """Test approval group with Unicode characters"""
        group_data = {
            "group_name": "テストグループ",  # Japanese
            "description": "これはテスト用の承認グループです"  # Japanese
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        assert response.status_code == 201
        created_group = response.json()
        assert created_group["group_name"] == group_data["group_name"]
        assert created_group["description"] == group_data["description"]
    
    async def test_approval_group_whitespace_handling(self, client: AsyncClient):
        """Test approval group with whitespace in fields"""
        group_data = {
            "group_name": "  Test Group  ",  # Leading/trailing spaces
            "description": "\n\tTest description\n\t"  # Tabs and newlines
        }
        
        response = await client.post(
            "/api/v1/approval-groups/",
            json=group_data
        )
        
        # Should either succeed as-is or trim whitespace
        assert response.status_code in [201, 422]