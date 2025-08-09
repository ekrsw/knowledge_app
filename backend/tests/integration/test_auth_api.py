"""
Authentication API Integration Tests

Tests for /api/v1/auth endpoints including login, registration, 
token validation, and user information retrieval.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def test_auth_user(db_session: AsyncSession):
    """Create a test user for authentication"""
    approval_group = await ApprovalGroupFactory.create_development_group(db_session)
    user = await UserFactory.create_user(
        db_session,
        username="authtest",
        email="authtest@example.com",
        full_name="Auth Test User",
        password="testpassword123"
    )
    return user


class TestAuthLogin:
    """Test authentication login endpoints"""
    
    async def test_login_oauth2_success(self, client: AsyncClient, test_auth_user):
        """Test successful OAuth2 login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "authtest",  # Using actual username
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify token structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    async def test_login_oauth2_invalid_email(self, client: AsyncClient, test_auth_user):
        """Test OAuth2 login with invalid email"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistentuser",
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_oauth2_invalid_password(self, client: AsyncClient, test_auth_user):
        """Test OAuth2 login with invalid password"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "authtest",
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_oauth2_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test OAuth2 login with inactive user"""
        # Create inactive user
        inactive_user = await UserFactory.create_user(
            db_session,
            username="inactivetest",
            email="inactive@example.com",
            password="testpassword123",
            is_active=False
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactivetest",
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "inactive" in data["detail"].lower()
    
    async def test_login_json_success(self, client: AsyncClient, test_auth_user):
        """Test successful JSON login"""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify token structure
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
    
    async def test_login_json_invalid_email(self, client: AsyncClient, test_auth_user):
        """Test JSON login with invalid email"""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "nonexistent@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_json_invalid_password(self, client: AsyncClient, test_auth_user):
        """Test JSON login with invalid password"""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_json_missing_fields(self, client: AsyncClient, test_auth_user):
        """Test JSON login with missing fields"""
        # Missing password
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com"
            }
        )
        
        assert response.status_code == 422
        
        # Missing email
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 422
        
        # Empty body
        response = await client.post(
            "/api/v1/auth/login/json",
            json={}
        )
        
        assert response.status_code == 422
    
    async def test_login_json_invalid_email_format(self, client: AsyncClient, test_auth_user):
        """Test JSON login with invalid email format"""
        response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "not-an-email",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestAuthRegistration:
    """Test user registration endpoints"""
    
    async def test_register_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful user registration"""
        # Create approval group for the new user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword123",
                "full_name": "New User",
                "sweet_name": "sweetname",
                "ctstage_name": "ctstagename"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify user data
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert data["sweet_name"] == "sweetname"
        assert data["ctstage_name"] == "ctstagename"
        assert data["role"] == "user"  # Default role
        assert data["is_active"] is True
        assert "id" in data
        assert "password_hash" not in data  # Password should not be returned
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_auth_user):
        """Test registration with duplicate username"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "authtest",  # Already exists
                "email": "different@example.com",
                "password": "newpassword123",
                "full_name": "Different User"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "username" in data["detail"].lower()
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_auth_user):
        """Test registration with duplicate email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": "authtest@example.com",  # Already exists
                "password": "newpassword123",
                "full_name": "Different User"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower()
    
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration with missing required fields"""
        # Missing username
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing email
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing password
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing full_name
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    async def test_register_invalid_email_format(self, client: AsyncClient):
        """Test registration with invalid email format"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with too short password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "123",  # Too short
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    


class TestAuthUserInfo:
    """Test authenticated user information endpoints"""
    
    async def test_get_current_user_success(self, authenticated_client: AsyncClient, test_users):
        """Test getting current user information with valid token"""
        response = await authenticated_client.get("/api/v1/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data structure
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "full_name" in data
        assert "role" in data
        assert "is_active" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify no sensitive data
        assert "password_hash" not in data
        
        # Verify the returned user is admin (from authenticated_client fixture)
        assert data["role"] == "admin"
    
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without authentication token"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
    
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestAuthTokenValidation:
    """Test token validation endpoints"""
    
    async def test_test_token_success(self, authenticated_client: AsyncClient, test_users):
        """Test token validation with valid token"""
        response = await authenticated_client.post("/api/v1/auth/test-token")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data is returned
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "role" in data
        assert data["role"] == "admin"  # From authenticated_client fixture
    
    async def test_test_token_no_token(self, client: AsyncClient):
        """Test token validation without token"""
        response = await client.post("/api/v1/auth/test-token")
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
    
    async def test_test_token_invalid_token(self, client: AsyncClient):
        """Test token validation with invalid token"""
        response = await client.post(
            "/api/v1/auth/test-token",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_test_token_expired_token(self, client: AsyncClient):
        """Test token validation with expired token"""
        # Create a token with very short expiration
        from tests.utils.auth import create_expired_token
        expired_token = await create_expired_token()
        
        response = await client.post(
            "/api/v1/auth/test-token",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "credential" in data["detail"].lower()


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""
    
    async def test_auth_header_variations(self, client: AsyncClient, test_auth_user):
        """Test different authentication header formats"""
        # Login to get token
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com",
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Test valid Bearer token
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Test invalid header format (missing Bearer)
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": token}
        )
        assert response.status_code == 403
        
        # Test empty Authorization header
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": ""}
        )
        assert response.status_code == 403
        
        # Test wrong scheme
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 403
    
    async def test_username_email_login_consistency(self, client: AsyncClient, test_auth_user):
        """Test that username and email login return consistent token"""
        # Login with username (OAuth2)
        oauth_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "authtest",
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert oauth_response.status_code == 200
        oauth_token = oauth_response.json()["access_token"]
        
        # Login with email (JSON)
        json_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com",
                "password": "testpassword123"
            }
        )
        assert json_response.status_code == 200
        json_token = json_response.json()["access_token"]
        
        # Both tokens should work for authenticated endpoints
        oauth_me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {oauth_token}"}
        )
        assert oauth_me_response.status_code == 200
        
        json_me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {json_token}"}
        )
        assert json_me_response.status_code == 200
        
        # User data should be identical
        oauth_user = oauth_me_response.json()
        json_user = json_me_response.json()
        assert oauth_user["id"] == json_user["id"]
        assert oauth_user["username"] == json_user["username"]
        assert oauth_user["email"] == json_user["email"]
    
    async def test_full_auth_flow(self, client: AsyncClient, test_auth_user):
        """Test complete authentication flow: login -> get user info -> validate token"""
        # Step 1: Login
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "authtest@example.com",
                "password": "testpassword123"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        
        # Step 2: Get user info with token
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        me_response = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == "authtest"
        assert me_data["email"] == "authtest@example.com"
        
        # Step 3: Validate token
        test_token_response = await client.post(
            "/api/v1/auth/test-token",
            headers=auth_headers
        )
        assert test_token_response.status_code == 200
        token_data = test_token_response.json()
        assert token_data["id"] == me_data["id"]
    
    async def test_register_and_login_flow(self, client: AsyncClient, db_session: AsyncSession):
        """Test user registration followed by login"""
        # Create approval group
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # Step 1: Register new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "flowtest",
                "email": "flowtest@example.com",
                "password": "flowtestpassword123",
                "full_name": "Flow Test User"
            }
        )
        
        assert register_response.status_code == 201
        register_data = register_response.json()
        
        # Step 2: Login with new user
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": "flowtest@example.com",
                "password": "flowtestpassword123"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        access_token = login_data["access_token"]
        
        # Step 3: Verify user info
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == "flowtest"
        assert me_data["email"] == "flowtest@example.com"
        assert me_data["id"] == register_data["id"]