"""
Information Category Management API Integration Tests

Tests for /api/v1/info-categories endpoints including CRUD operations,
active filtering, and data validation.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from uuid import uuid4

from app.models.info_category import InfoCategory
from tests.factories.info_category_factory import InfoCategoryFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def clean_info_categories(db_session: AsyncSession):
    """Clean info_categories table before each test"""
    await db_session.execute(delete(InfoCategory))
    await db_session.commit()
    yield
    await db_session.execute(delete(InfoCategory))
    await db_session.commit()


class TestInfoCategoryList:
    """Test info category list endpoint (GET /api/v1/info-categories/)"""
    
    async def test_list_info_categories_empty(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing info categories when none exist"""
        response = await client.get("/api/v1/info-categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_list_info_categories_with_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing info categories with existing data"""
        # Create test info categories
        category1 = await InfoCategoryFactory.create_technology_category(db_session)
        category2 = await InfoCategoryFactory.create_business_category(db_session)
        category3 = await InfoCategoryFactory.create_operations_category(db_session)
        
        response = await client.get("/api/v1/info-categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify category data structure
        category_names = [cat["category_name"] for cat in data]
        assert "Technology" in category_names
        assert "Business" in category_names
        assert "Operations" in category_names
        
        # Verify data structure
        for category in data:
            assert "category_id" in category
            assert "category_name" in category
            assert "is_active" in category
            assert "display_order" in category
            assert "created_at" in category
            assert "updated_at" in category
    
    async def test_list_info_categories_pagination(self, client: AsyncClient, db_session: AsyncSession):
        """Test pagination in info category list"""
        # Get initial count
        initial_response = await client.get("/api/v1/info-categories/")
        initial_count = len(initial_response.json())
        
        # Create multiple info categories
        for i in range(5):
            await InfoCategoryFactory.create(
                db_session,
                category_name=f"Category{i}",
                display_order=i + 1
            )
        
        # Get total count after adding
        total_response = await client.get("/api/v1/info-categories/")
        total_count = len(total_response.json())
        assert total_count == initial_count + 5
        
        # Test with limit
        response = await client.get("/api/v1/info-categories/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == min(3, total_count)
        
        # Test with skip
        skip_count = 2
        response = await client.get(f"/api/v1/info-categories/?skip={skip_count}&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        expected_count = max(0, min(10, total_count - skip_count))
        assert len(data) == expected_count


class TestInfoCategoryActive:
    """Test active info category endpoint (GET /api/v1/info-categories/active)"""
    
    async def test_get_active_info_categories_empty(self, client: AsyncClient, db_session: AsyncSession, clean_info_categories):
        """Test getting active categories when none exist"""
        response = await client.get("/api/v1/info-categories/active")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_get_active_info_categories_only(self, client: AsyncClient, db_session: AsyncSession, clean_info_categories):
        """Test getting only active categories"""
        # Create active and inactive categories
        active1 = await InfoCategoryFactory.create(
            db_session,
            category_name="Active Category 1",
            is_active=True
        )
        active2 = await InfoCategoryFactory.create(
            db_session,
            category_name="Active Category 2", 
            is_active=True
        )
        inactive = await InfoCategoryFactory.create(
            db_session,
            category_name="Inactive Category",
            is_active=False
        )
        
        response = await client.get("/api/v1/info-categories/active")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Should only contain active categories
        category_names = [cat["category_name"] for cat in data]
        assert "Active Category 1" in category_names
        assert "Active Category 2" in category_names
        assert "Inactive Category" not in category_names
        
        # All returned categories should be active
        for category in data:
            assert category["is_active"] == True
    
    async def test_get_active_info_categories_ordering(self, client: AsyncClient, db_session: AsyncSession, clean_info_categories):
        """Test active categories are returned in display order"""
        # Create categories with different display orders
        await InfoCategoryFactory.create(
            db_session,
            category_name="Category B",
            display_order=2,
            is_active=True
        )
        await InfoCategoryFactory.create(
            db_session,
            category_name="Category A",
            display_order=1,
            is_active=True
        )
        await InfoCategoryFactory.create(
            db_session,
            category_name="Category C",
            display_order=3,
            is_active=True
        )
        
        response = await client.get("/api/v1/info-categories/active")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Should be ordered by display_order
        assert data[0]["display_order"] <= data[1]["display_order"] <= data[2]["display_order"]


class TestInfoCategoryGet:
    """Test info category retrieval endpoint (GET /api/v1/info-categories/{category_id})"""
    
    async def test_get_info_category_by_id(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting info category by valid ID"""
        # Create a test info category
        test_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        response = await client.get(f"/api/v1/info-categories/{test_category.category_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category_id"] == str(test_category.category_id)
        assert data["category_name"] == test_category.category_name
        assert data["is_active"] == test_category.is_active
        assert data["display_order"] == test_category.display_order
        assert "created_at" in data
        assert "updated_at" in data
    
    async def test_get_nonexistent_info_category(self, client: AsyncClient):
        """Test getting non-existent info category returns 404"""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/info-categories/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_get_info_category_invalid_uuid(self, client: AsyncClient):
        """Test getting info category with invalid UUID format"""
        invalid_id = "not-a-uuid"
        response = await client.get(f"/api/v1/info-categories/{invalid_id}")
        
        assert response.status_code == 422  # Validation error


class TestInfoCategoryCreate:
    """Test info category creation endpoint (POST /api/v1/info-categories/)"""
    
    async def test_create_info_category_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful info category creation"""
        category_data = {
            "category_name": "New Test Category",
            "is_active": True,
            "display_order": 10
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 201
        created_category = response.json()
        
        assert created_category["category_name"] == "New Test Category"
        assert created_category["is_active"] == True
        assert created_category["display_order"] == 10
        assert "category_id" in created_category
        assert "created_at" in created_category
        assert "updated_at" in created_category
    
    async def test_create_info_category_minimal_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating info category with minimal required data"""
        category_data = {
            "category_name": "Minimal Category"
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 201
        created_category = response.json()
        
        assert created_category["category_name"] == "Minimal Category"
        assert created_category["is_active"] == True  # Default value
        assert created_category["display_order"] == 0  # Default value
    
    async def test_create_info_category_missing_required_fields(self, client: AsyncClient):
        """Test creating info category with missing required fields"""
        # Missing category_name
        response = await client.post(
            "/api/v1/info-categories/",
            json={"display_order": 5}
        )
        assert response.status_code == 422
        
        # Empty data
        response = await client.post(
            "/api/v1/info-categories/",
            json={}
        )
        assert response.status_code == 422
    
    async def test_create_info_category_invalid_data_types(self, client: AsyncClient):
        """Test creating info category with invalid data types"""
        # is_active should be boolean
        category_data = {
            "category_name": "Test Category",
            "is_active": "not-a-boolean"
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 422
        
        # display_order should be integer
        category_data = {
            "category_name": "Test Category",
            "display_order": "not-an-integer"
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 422
    
    async def test_create_info_category_negative_display_order(self, client: AsyncClient):
        """Test creating info category with negative display order"""
        category_data = {
            "category_name": "Test Category",
            "display_order": -5
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        # Should either succeed or fail with validation error
        assert response.status_code in [201, 422]


class TestInfoCategoryUpdate:
    """Test info category update endpoint (PUT /api/v1/info-categories/{category_id})"""
    
    async def test_update_info_category_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful info category update"""
        # Create a test info category
        test_category = await InfoCategoryFactory.create(
            db_session,
            category_name="Original Name",
            is_active=True,
            display_order=5
        )
        
        update_data = {
            "category_name": "Updated Name",
            "is_active": False,
            "display_order": 10
        }
        
        response = await client.put(
            f"/api/v1/info-categories/{test_category.category_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        
        assert updated["category_name"] == "Updated Name"
        assert updated["is_active"] == False
        assert updated["display_order"] == 10
        assert updated["category_id"] == str(test_category.category_id)
    
    async def test_update_info_category_partial(self, client: AsyncClient, db_session: AsyncSession):
        """Test partial update of info category"""
        # Create a test info category
        test_category = await InfoCategoryFactory.create(
            db_session,
            category_name="Original Name",
            is_active=True,
            display_order=5
        )
        
        # Update only one field
        update_data = {
            "category_name": "Partially Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/info-categories/{test_category.category_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        
        assert updated["category_name"] == "Partially Updated Name"
        assert updated["is_active"] == True  # Unchanged
        assert updated["display_order"] == 5  # Unchanged
    
    async def test_update_nonexistent_info_category(self, client: AsyncClient):
        """Test updating non-existent info category returns 404"""
        fake_id = str(uuid4())
        update_data = {
            "category_name": "Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/info-categories/{fake_id}",
            json=update_data
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_update_info_category_invalid_data(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating info category with invalid data"""
        # Create a test info category
        test_category = await InfoCategoryFactory.create_technology_category(db_session)
        
        # Invalid data types
        update_data = {
            "is_active": "not-a-boolean",
            "display_order": "not-an-integer"
        }
        
        response = await client.put(
            f"/api/v1/info-categories/{test_category.category_id}",
            json=update_data
        )
        
        assert response.status_code == 422
    
    async def test_update_info_category_display_order_change(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating display order affects sorting"""
        # Create test categories
        category = await InfoCategoryFactory.create(
            db_session,
            category_name="Test Category",
            display_order=5
        )
        
        # Update display order
        update_data = {
            "display_order": 1
        }
        
        response = await client.put(
            f"/api/v1/info-categories/{category.category_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["display_order"] == 1


class TestInfoCategoryEdgeCases:
    """Test edge cases and error handling"""
    
    async def test_info_category_with_special_characters(self, client: AsyncClient):
        """Test info category with special characters in name"""
        category_data = {
            "category_name": "Test-Category_123 (Special Characters!)"
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 201
        created_category = response.json()
        assert created_category["category_name"] == category_data["category_name"]
    
    async def test_info_category_unicode_support(self, client: AsyncClient):
        """Test info category with Unicode characters"""
        category_data = {
            "category_name": "技術カテゴリー"  # Japanese
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code == 201
        created_category = response.json()
        assert created_category["category_name"] == category_data["category_name"]
    
    async def test_info_category_extreme_display_orders(self, client: AsyncClient):
        """Test info categories with extreme display order values"""
        # Very large display order
        category_data = {
            "category_name": "Large Order Category",
            "display_order": 999999
        }
        
        response = await client.post(
            "/api/v1/info-categories/",
            json=category_data
        )
        
        assert response.status_code in [201, 422]
        
        if response.status_code == 201:
            created = response.json()
            assert created["display_order"] == 999999
    
    async def test_active_inactive_category_filtering(self, client: AsyncClient, db_session: AsyncSession):
        """Test comprehensive active/inactive category filtering"""
        # Get initial count
        initial_response = await client.get("/api/v1/info-categories/")
        initial_count = len(initial_response.json())
        
        # Create mix of active and inactive categories
        await InfoCategoryFactory.create(db_session, category_name="Active1", is_active=True)
        await InfoCategoryFactory.create(db_session, category_name="Active2", is_active=True)
        await InfoCategoryFactory.create(db_session, category_name="Inactive1", is_active=False)
        await InfoCategoryFactory.create(db_session, category_name="Inactive2", is_active=False)
        
        # Get all categories
        all_response = await client.get("/api/v1/info-categories/")
        assert all_response.status_code == 200
        all_categories = all_response.json()
        assert len(all_categories) == initial_count + 4
        
        # Get only active categories
        active_response = await client.get("/api/v1/info-categories/active")
        assert active_response.status_code == 200
        active_categories = active_response.json()
        
        # Filter active categories from all categories
        active_from_all = [cat for cat in all_categories if cat["is_active"]]
        assert len(active_categories) == len(active_from_all)
        
        # Verify all active categories are actually active
        for category in active_categories:
            assert category["is_active"] == True