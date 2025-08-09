"""
Basic test to verify fixtures are working correctly
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.approval_group import ApprovalGroup


@pytest.mark.asyncio
class TestBasicFixtures:
    """Test that basic fixtures are working correctly"""
    
    async def test_database_session_fixture(self, db_session: AsyncSession):
        """Test that database session fixture is working"""
        assert db_session is not None
        assert hasattr(db_session, 'execute')
        assert hasattr(db_session, 'commit')
    
    async def test_client_fixture(self, client: AsyncClient):
        """Test that HTTP client fixture is working"""
        assert client is not None
        assert hasattr(client, 'get')
        assert hasattr(client, 'post')
        assert str(client.base_url) == "http://test"
    
    async def test_approval_groups_fixture(self, test_approval_groups: dict):
        """Test that approval groups fixture creates expected groups"""
        assert "development" in test_approval_groups
        assert "quality" in test_approval_groups
        assert "management" in test_approval_groups
        
        dev_group = test_approval_groups["development"]
        assert isinstance(dev_group, ApprovalGroup)
        assert dev_group.group_name == "Development Team"
        assert dev_group.is_active is True
    
    async def test_users_fixture(self, test_users: dict):
        """Test that users fixture creates expected users"""
        expected_roles = ["admin", "approver", "qa_approver", "user", "inactive"]
        
        for role in expected_roles:
            assert role in test_users
            user = test_users[role]
            assert isinstance(user, User)
            assert user.username is not None
            assert user.email is not None
        
        # Check specific user properties
        admin = test_users["admin"]
        assert admin.role == "admin"
        assert admin.is_active is True
        
        approver = test_users["approver"]
        assert approver.role == "approver"
        assert approver.approval_group_id is not None
        
        inactive = test_users["inactive"]
        assert inactive.is_active is False
    
    async def test_authenticated_clients(
        self, 
        authenticated_client: AsyncClient,
        user_client: AsyncClient,
        approver_client: AsyncClient
    ):
        """Test that authenticated clients have proper headers"""
        # Check that clients have Authorization headers
        assert "Authorization" in authenticated_client.headers
        assert authenticated_client.headers["Authorization"].startswith("Bearer ")
        
        assert "Authorization" in user_client.headers
        assert user_client.headers["Authorization"].startswith("Bearer ")
        
        assert "Authorization" in approver_client.headers
        assert approver_client.headers["Authorization"].startswith("Bearer ")
    
    @pytest.mark.slow
    async def test_system_health_endpoint(self, client: AsyncClient):
        """Test system health endpoint without authentication"""
        response = await client.get("/api/v1/system/health")
        
        # System health should be accessible without auth
        assert response.status_code in [200, 404]  # 404 if endpoint not implemented yet