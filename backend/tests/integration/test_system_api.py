"""
System API Integration Tests

Tests for /api/v1/system endpoints including health check, version info,
system stats, configuration, maintenance tasks, and API documentation.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory
from tests.factories.revision_factory import RevisionFactory
from tests.factories.notification_factory import NotificationFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession):
    """Create a test admin user"""
    approval_group = await ApprovalGroupFactory.create_development_group(db_session)
    admin_user = await UserFactory.create_admin(
        db_session,
        username="admin",
        email="admin@example.com",
        approval_group=approval_group
    )
    return admin_user


@pytest_asyncio.fixture
async def test_regular_user(db_session: AsyncSession):
    """Create a test regular user"""
    approval_group = await ApprovalGroupFactory.create_development_group(db_session)
    regular_user = await UserFactory.create_user(
        db_session,
        username="regular",
        email="regular@example.com",
        approval_group=approval_group
    )
    return regular_user


@pytest_asyncio.fixture
async def authenticated_admin_client(client: AsyncClient, test_admin_user):
    """Client authenticated with admin user"""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture
async def authenticated_user_client(client: AsyncClient, test_regular_user):
    """Client authenticated with regular user"""
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "regular",
            "password": "testpassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


class TestSystemHealth:
    """Test system health endpoints"""
    
    async def test_health_check_public(self, client: AsyncClient):
        """Test health check endpoint (public access)"""
        response = await client.get("/api/v1/system/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "database" in data
        
        # Check values
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["database"] == "connected"
    
    async def test_version_info_public(self, client: AsyncClient):
        """Test version info endpoint (public access)"""
        response = await client.get("/api/v1/system/version")
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "version" in data
        assert "api_version" in data
        assert "build_date" in data
        assert "features" in data
        
        # Check values
        assert data["version"] == "0.1.0"
        assert data["api_version"] == "v1"
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0


class TestSystemStats:
    """Test system statistics endpoints"""
    
    async def test_get_system_stats_admin_success(self, authenticated_admin_client, db_session):
        """Test getting system stats as admin"""
        # Create some test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        user = await UserFactory.create_user(db_session, approval_group=approval_group)
        revision = await RevisionFactory.create_draft(db_session, proposer=user, approver=user)
        notification = await NotificationFactory.create(db_session, user=user, revision=revision)
        
        response = await authenticated_admin_client.get("/api/v1/system/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "users" in data
        assert "revisions" in data
        assert "notifications" in data
        assert "system" in data
        
        # Check user stats
        assert "total_users" in data["users"]
        assert "by_role" in data["users"]
        assert data["users"]["total_users"] > 0
        
        # Check revision stats
        assert "total_revisions" in data["revisions"]
        assert "by_status" in data["revisions"]
        assert data["revisions"]["total_revisions"] > 0
        
        # Check notification stats
        assert "total_notifications" in data["notifications"]
        assert "unread_count" in data["notifications"]
        assert "read_count" in data["notifications"]
        assert data["notifications"]["total_notifications"] > 0
        
        # Check system info
        assert "database_status" in data["system"]
        assert "api_status" in data["system"]
        assert "last_updated" in data["system"]
    
    async def test_get_system_stats_regular_user_forbidden(self, authenticated_user_client):
        """Test getting system stats as regular user should be forbidden"""
        response = await authenticated_user_client.get("/api/v1/system/stats")
        
        assert response.status_code == 403
    
    async def test_get_system_stats_unauthenticated(self, client: AsyncClient):
        """Test getting system stats without authentication"""
        response = await client.get("/api/v1/system/stats")
        
        assert response.status_code == 401


# Removed: System config and maintenance tests for deleted endpoints


class TestSystemDocumentation:
    """Test system API documentation endpoints"""
    
    async def test_get_api_documentation_public(self, client: AsyncClient):
        """Test getting API documentation (public access)"""
        response = await client.get("/api/v1/system/api-documentation")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "api_version" in data
        assert "base_url" in data
        assert "total_endpoints" in data
        assert "endpoint_groups" in data
        assert "authentication" in data
        assert "documentation" in data
        
        # Check values
        assert data["api_version"] == "v1"
        assert data["base_url"] == "/api/v1"
        assert isinstance(data["total_endpoints"], int)
        assert data["total_endpoints"] > 0
        
        # Check endpoint groups
        endpoint_groups = data["endpoint_groups"]
        expected_groups = [
            "authentication", "proposals", "approvals", "diffs",
            "notifications", "users", "system"
        ]
        
        for group in expected_groups:
            assert group in endpoint_groups
            assert "prefix" in endpoint_groups[group]
            assert "endpoints" in endpoint_groups[group]
            assert isinstance(endpoint_groups[group]["endpoints"], list)
            assert len(endpoint_groups[group]["endpoints"]) > 0


class TestSystemEndpointsIntegration:
    """Test system endpoints integration scenarios"""
    
    async def test_admin_full_system_access(self, authenticated_admin_client, db_session):
        """Test admin can access all system endpoints"""
        # Create some test data
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        user = await UserFactory.create_user(db_session, approval_group=approval_group)
        
        # Health check
        health_response = await authenticated_admin_client.get("/api/v1/system/health")
        assert health_response.status_code == 200
        
        # Version info
        version_response = await authenticated_admin_client.get("/api/v1/system/version")
        assert version_response.status_code == 200
        
        # System stats
        stats_response = await authenticated_admin_client.get("/api/v1/system/stats")
        assert stats_response.status_code == 200
        
        # API documentation
        docs_response = await authenticated_admin_client.get("/api/v1/system/api-documentation")
        assert docs_response.status_code == 200
    
    async def test_regular_user_limited_system_access(self, authenticated_user_client):
        """Test regular user has limited access to system endpoints"""
        # Public endpoints should work
        health_response = await authenticated_user_client.get("/api/v1/system/health")
        assert health_response.status_code == 200
        
        version_response = await authenticated_user_client.get("/api/v1/system/version")
        assert version_response.status_code == 200
        
        docs_response = await authenticated_user_client.get("/api/v1/system/api-documentation")
        assert docs_response.status_code == 200
        
        # Admin-only endpoints should be forbidden
        stats_response = await authenticated_user_client.get("/api/v1/system/stats")
        assert stats_response.status_code == 403
        
        # Removed: config and maintenance endpoints tests