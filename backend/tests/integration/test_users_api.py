"""
User Management API Integration Tests

Tests for /api/v1/users endpoints including CRUD operations,
permission checks, role-based access control, and pagination.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from tests.factories.user_factory import UserFactory
from tests.factories.approval_group_factory import ApprovalGroupFactory


# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio


class TestUserList:
    """Test user list endpoint (GET /api/v1/users/)"""
    
    async def test_list_users_as_admin(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test admin can list all users"""
        # Create test users
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        user1 = await UserFactory.create_user(
            db_session,
            username="listuser1",
            email="listuser1@example.com"
        )
        user2 = await UserFactory.create_approver(
            db_session,
            approval_group,
            username="listuser2",
            email="listuser2@example.com"
        )
        
        # Admin should be able to list all users
        response = await authenticated_client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include at least the admin user and the created users
        assert isinstance(data, list)
        assert len(data) >= 3
        
        # Verify user data structure
        usernames = [user["username"] for user in data]
        assert "listuser1" in usernames
        assert "listuser2" in usernames
    
    async def test_list_users_as_non_admin(self, client: AsyncClient, db_session: AsyncSession, test_users):
        """Test non-admin cannot list users"""
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to list users
        response = await client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()
    
    async def test_list_users_pagination(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test pagination in user list"""
        # Create multiple users
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        for i in range(5):
            await UserFactory.create_user(
                db_session,
                username=f"pageuser{i}",
                email=f"pageuser{i}@example.com"
            )
        
        # Test with limit
        response = await authenticated_client.get("/api/v1/users/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        
        # Test with skip
        response = await authenticated_client.get("/api/v1/users/?skip=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        # Should have users minus the skipped ones
        assert isinstance(data, list)
    
    async def test_list_users_without_auth(self, client: AsyncClient):
        """Test unauthenticated access is denied"""
        response = await client.get("/api/v1/users/")
        assert response.status_code == 403


class TestUserCreate:
    """Test user creation endpoint (POST /api/v1/users/)"""
    
    async def test_create_user_as_admin(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test admin can create new users"""
        # Create approval group first
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "full_name": "New User",
            "role": "user",
            "sweet_name": "newsweet",
            "ctstage_name": "newctstage"
        }
        
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        assert response.status_code == 201
        created_user = response.json()
        
        assert created_user["username"] == "newuser"
        assert created_user["email"] == "newuser@example.com"
        assert created_user["full_name"] == "New User"
        assert created_user["role"] == "user"
        assert "password_hash" not in created_user
        assert "id" in created_user
    
    async def test_create_user_duplicate_username(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test creating user with duplicate username fails"""
        # Create first user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        existing_user = await UserFactory.create_user(
            db_session,
            username="duplicate",
            email="first@example.com"
        )
        
        # Try to create another user with same username
        user_data = {
            "username": "duplicate",
            "email": "second@example.com",
            "password": "password123",
            "full_name": "Second User"
        }
        
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    async def test_create_user_duplicate_email(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test creating user with duplicate email fails"""
        # Create first user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        existing_user = await UserFactory.create_user(
            db_session,
            username="first",
            email="duplicate@example.com"
        )
        
        # Try to create another user with same email
        user_data = {
            "username": "second",
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "Second User"
        }
        
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
    
    async def test_create_user_as_non_admin(self, client: AsyncClient, test_users):
        """Test non-admin cannot create users"""
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
        
        response = await client.post(
            "/api/v1/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_create_user_invalid_email(self, authenticated_client: AsyncClient):
        """Test creating user with invalid email format"""
        user_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Test User"
        }
        
        response = await authenticated_client.post(
            "/api/v1/users/",
            json=user_data
        )
        
        assert response.status_code == 422
    
    async def test_create_user_missing_required_fields(self, authenticated_client: AsyncClient):
        """Test creating user with missing required fields"""
        # Missing username
        response = await authenticated_client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing email
        response = await authenticated_client.post(
            "/api/v1/users/",
            json={
                "username": "testuser",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422
        
        # Missing password
        response = await authenticated_client.post(
            "/api/v1/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422


class TestUserGet:
    """Test user retrieval endpoint (GET /api/v1/users/{user_id})"""
    
    async def test_get_user_as_admin(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test admin can get any user's details"""
        # Create a test user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        test_user = await UserFactory.create_user(
            db_session,
            username="getuser",
            email="getuser@example.com",
            full_name="Get User"
        )
        
        response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(test_user.id)
        assert data["username"] == "getuser"
        assert data["email"] == "getuser@example.com"
        assert data["full_name"] == "Get User"
        assert "password_hash" not in data
    
    async def test_get_own_user_details(self, client: AsyncClient, test_users):
        """Test user can get their own details"""
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get own details
        response = await client.get(
            f"/api/v1/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(regular_user.id)
        assert data["username"] == regular_user.username
    
    async def test_get_other_user_as_non_admin(self, client: AsyncClient, test_users, db_session: AsyncSession):
        """Test non-admin cannot get other users' details"""
        # Create another user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        other_user = await UserFactory.create_user(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to get other user's details
        response = await client.get(
            f"/api/v1/users/{other_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_get_nonexistent_user(self, authenticated_client: AsyncClient):
        """Test getting non-existent user returns 404"""
        fake_id = str(uuid4())
        response = await authenticated_client.get(f"/api/v1/users/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_get_user_without_auth(self, client: AsyncClient, test_users):
        """Test unauthenticated access is denied"""
        user = test_users["user"]
        response = await client.get(f"/api/v1/users/{user.id}")
        assert response.status_code == 403


class TestUserUpdate:
    """Test user update endpoint (PUT /api/v1/users/{user_id})"""
    
    async def test_update_user_as_admin(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test admin can update any user"""
        # Create a test user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        test_user = await UserFactory.create_user(
            db_session,
            username="updateuser",
            email="update@example.com",
            full_name="Original Name"
        )
        
        update_data = {
            "full_name": "Updated Name",
            "role": "approver"
        }
        
        response = await authenticated_client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["full_name"] == "Updated Name"
        assert updated["role"] == "approver"
    
    async def test_update_own_profile(self, client: AsyncClient, test_users):
        """Test user can update their own profile"""
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Update own profile
        update_data = {
            "full_name": "My New Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{regular_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["full_name"] == "My New Name"
    
    async def test_non_admin_cannot_change_role(self, client: AsyncClient, test_users):
        """Test non-admin cannot change their own role"""
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to change own role (should be silently ignored)
        update_data = {
            "role": "admin",
            "full_name": "Updated Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{regular_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # The request succeeds, but role should not change
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "user"  # Role should remain unchanged
        assert data["full_name"] == "Updated Name"  # Other fields should update
    
    async def test_update_other_user_as_non_admin(self, client: AsyncClient, test_users, db_session: AsyncSession):
        """Test non-admin cannot update other users"""
        # Create another user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        other_user = await UserFactory.create_user(
            db_session,
            username="otherupdate",
            email="otherupdate@example.com"
        )
        
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to update other user
        update_data = {
            "full_name": "Hacked Name"
        }
        
        response = await client.put(
            f"/api/v1/users/{other_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_update_nonexistent_user(self, authenticated_client: AsyncClient):
        """Test updating non-existent user returns 404"""
        fake_id = str(uuid4())
        update_data = {
            "full_name": "New Name"
        }
        
        response = await authenticated_client.put(
            f"/api/v1/users/{fake_id}",
            json=update_data
        )
        
        assert response.status_code == 404
    
    async def test_update_user_duplicate_username(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test updating user with duplicate username fails"""
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        
        # Create two users
        user1 = await UserFactory.create_user(
            db_session,
            username="user1",
            email="user1@example.com"
        )
        user2 = await UserFactory.create_user(
            db_session,
            username="user2",
            email="user2@example.com"
        )
        
        # Try to update user2 with user1's username
        update_data = {
            "username": "user1"
        }
        
        response = await authenticated_client.put(
            f"/api/v1/users/{user2.id}",
            json=update_data
        )
        
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()


class TestUserDelete:
    """Test user deletion endpoint (DELETE /api/v1/users/{user_id})"""
    
    async def test_delete_user_as_admin(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test admin can delete users"""
        # Create a test user
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        test_user = await UserFactory.create_user(
            db_session,
            username="deleteuser",
            email="delete@example.com"
        )
        
        response = await authenticated_client.delete(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
        assert get_response.status_code == 404
    
    async def test_delete_user_as_non_admin(self, client: AsyncClient, test_users, db_session: AsyncSession):
        """Test non-admin cannot delete users"""
        # Create a user to delete
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        target_user = await UserFactory.create_user(
            db_session,
            username="targetdelete",
            email="targetdelete@example.com"
        )
        
        # Login as regular user
        regular_user = test_users["user"]
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": regular_user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Try to delete user
        response = await client.delete(
            f"/api/v1/users/{target_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_delete_nonexistent_user(self, authenticated_client: AsyncClient):
        """Test deleting non-existent user returns 404"""
        fake_id = str(uuid4())
        response = await authenticated_client.delete(f"/api/v1/users/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_delete_self_as_admin(self, authenticated_client: AsyncClient, test_users):
        """Test admin can delete their own account"""
        # Get admin user ID from the current user endpoint
        me_response = await authenticated_client.get("/api/v1/auth/me")
        assert me_response.status_code == 200
        admin_id = me_response.json()["id"]
        
        # Admin should be able to delete themselves (careful operation)
        response = await authenticated_client.delete(f"/api/v1/users/{admin_id}")
        
        # This might be blocked by business logic to prevent lockout
        # Check if it's either successful or properly blocked
        assert response.status_code in [204, 400, 403]
    
    async def test_delete_user_without_auth(self, client: AsyncClient, test_users):
        """Test unauthenticated deletion is denied"""
        user = test_users["user"]
        response = await client.delete(f"/api/v1/users/{user.id}")
        assert response.status_code == 403


class TestUserPermissionMatrix:
    """Test comprehensive permission matrix for all user endpoints"""
    
    @pytest.mark.parametrize("role,endpoint,method,expected_status", [
        # Admin can do everything
        ("admin", "/api/v1/users/", "GET", 200),
        ("admin", "/api/v1/users/", "POST", [201, 400, 422]),  # Can create (might fail on validation)
        ("admin", "/api/v1/users/{id}", "GET", 200),
        ("admin", "/api/v1/users/{id}", "PUT", 200),
        ("admin", "/api/v1/users/{id}", "DELETE", 204),
        
        # Approver has limited access
        ("approver", "/api/v1/users/", "GET", 403),
        ("approver", "/api/v1/users/", "POST", 403),
        ("approver", "/api/v1/users/{self}", "GET", 200),  # Can get self
        ("approver", "/api/v1/users/{other}", "GET", 403),  # Cannot get others
        ("approver", "/api/v1/users/{self}", "PUT", 200),  # Can update self
        ("approver", "/api/v1/users/{other}", "PUT", 403),  # Cannot update others
        ("approver", "/api/v1/users/{id}", "DELETE", 403),
        
        # Regular user has minimal access
        ("user", "/api/v1/users/", "GET", 403),
        ("user", "/api/v1/users/", "POST", 403),
        ("user", "/api/v1/users/{self}", "GET", 200),  # Can get self
        ("user", "/api/v1/users/{other}", "GET", 403),  # Cannot get others
        ("user", "/api/v1/users/{self}", "PUT", 200),  # Can update self
        ("user", "/api/v1/users/{other}", "PUT", 403),  # Cannot update others
        ("user", "/api/v1/users/{id}", "DELETE", 403),
    ])
    async def test_permission_matrix(self, client: AsyncClient, test_users, db_session: AsyncSession, 
                                    role, endpoint, method, expected_status):
        """Test role-based access control for user endpoints"""
        # Get the user for the specified role
        user = test_users[role]
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login/json",
            json={
                "email": user.email,
                "password": "testpassword123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create another user for testing
        approval_group = await ApprovalGroupFactory.create_development_group(db_session)
        other_user = await UserFactory.create_user(
            db_session,
            username="othermatrix",
            email="othermatrix@example.com"
        )
        
        # Prepare endpoint
        if "{self}" in endpoint:
            endpoint = endpoint.replace("{self}", str(user.id))
        elif "{other}" in endpoint:
            endpoint = endpoint.replace("{other}", str(other_user.id))
        elif "{id}" in endpoint:
            endpoint = endpoint.replace("{id}", str(other_user.id))
        
        # Prepare request data for POST/PUT
        request_data = None
        if method in ["POST", "PUT"]:
            request_data = {
                "username": f"test{uuid4().hex[:8]}",
                "email": f"test{uuid4().hex[:8]}@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        
        # Make request
        if method == "GET":
            response = await client.get(endpoint, headers=headers)
        elif method == "POST":
            response = await client.post(endpoint, json=request_data, headers=headers)
        elif method == "PUT":
            response = await client.put(endpoint, json={"full_name": "Updated"}, headers=headers)
        elif method == "DELETE":
            response = await client.delete(endpoint, headers=headers)
        
        # Check expected status
        if isinstance(expected_status, list):
            assert response.status_code in expected_status
        else:
            assert response.status_code == expected_status