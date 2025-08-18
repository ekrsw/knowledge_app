"""
Integration tests for user password update endpoint
"""
import pytest
from httpx import AsyncClient
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import user_repository
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash
from tests.utils.auth import create_auth_headers


@pytest.mark.asyncio
class TestUserPasswordUpdate:
    """Test cases for user password update"""
    
    async def test_update_own_password_success(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_users: dict
    ):
        """Test successful password update for own account"""
        # Get auth headers for regular user
        auth_headers = await create_auth_headers(test_users["user"])
        test_user_id = test_users["user"].id
        
        # Update password
        response = await client.put(
            f"/api/v1/users/{test_user_id}/password",
            json={
                "current_password": "testpassword123",
                "new_password": "NewTestPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user_id)
        # Password hash should not be in response
        assert "password_hash" not in data
    
    async def test_update_own_password_with_wrong_current_password(
        self, 
        client: AsyncClient, 
        test_users: dict
    ):
        """Test password update fails with wrong current password"""
        auth_headers = await create_auth_headers(test_users["user"])
        test_user_id = test_users["user"].id
        
        response = await client.put(
            f"/api/v1/users/{test_user_id}/password",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewTestPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect current password"
    
    async def test_update_other_user_password_as_regular_user(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_users: dict
    ):
        """Test regular user cannot update another user's password"""
        auth_headers = await create_auth_headers(test_users["user"])
        
        # Create another user
        other_user = await user_repository.create_with_password(
            db_session,
            obj_in=UserCreate(
                username="otheruser",
                email="other@example.com",
                password="OtherPass123!",
                full_name="Other User",
                role="user"
            )
        )
        
        # Try to update other user's password
        response = await client.put(
            f"/api/v1/users/{other_user.id}/password",
            json={
                "current_password": "OtherPass123!",
                "new_password": "NewOtherPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Users can only update their own password" in response.json()["detail"]
    
    async def test_admin_cannot_use_regular_password_endpoint_for_others(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test admin cannot use regular password endpoint for other users"""
        # Create a regular user
        regular_user = await user_repository.create_with_password(
            db_session,
            obj_in=UserCreate(
                username="regularuser",
                email="regular@example.com",
                password="RegularPass123!",
                full_name="Regular User",
                role="user"
            )
        )
        
        # Admin tries to use regular password endpoint for other user (should fail)
        response = await authenticated_client.put(
            f"/api/v1/users/{regular_user.id}/password",
            json={
                "current_password": "RegularPass123!",
                "new_password": "NewRegularPass456!"
            }
        )
        
        assert response.status_code == 403
        assert "Admins should use /admin-reset-password endpoint" in response.json()["detail"]
    
    async def test_update_password_for_nonexistent_user(
        self, 
        authenticated_client: AsyncClient
    ):
        """Test password update for non-existent user returns 403 due to permission check"""
        fake_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = await authenticated_client.put(
            f"/api/v1/users/{fake_user_id}/password",
            json={
                "current_password": "SomePassword123!",
                "new_password": "NewPassword456!"
            }
        )
        
        # Permission check happens before user existence check
        assert response.status_code == 403
        assert "Users can only update their own password" in response.json()["detail"]
    
    async def test_update_password_with_short_new_password(
        self, 
        client: AsyncClient, 
        test_users: dict
    ):
        """Test password update fails with too short new password"""
        auth_headers = await create_auth_headers(test_users["user"])
        test_user_id = test_users["user"].id
        
        response = await client.put(
            f"/api/v1/users/{test_user_id}/password",
            json={
                "current_password": "testpassword123",
                "new_password": "Short1!"  # Less than 8 characters
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_update_password_without_auth(
        self, 
        client: AsyncClient,
        test_users: dict
    ):
        """Test password update requires authentication"""
        test_user_id = test_users["user"].id
        
        response = await client.put(
            f"/api/v1/users/{test_user_id}/password",
            json={
                "current_password": "testpassword123",
                "new_password": "NewTestPass456!"
            }
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    
    async def test_password_actually_changes_in_database(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_users: dict
    ):
        """Test that password is actually updated in the database"""
        auth_headers = await create_auth_headers(test_users["user"])
        test_user_id = test_users["user"].id
        
        # Get original password hash
        user_before = await user_repository.get(db_session, id=test_user_id)
        original_hash = user_before.password_hash
        
        # Update password
        response = await client.put(
            f"/api/v1/users/{test_user_id}/password",
            json={
                "current_password": "testpassword123",
                "new_password": "NewTestPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check password hash changed in database
        user_after = await user_repository.get(db_session, id=test_user_id)
        assert user_after.password_hash != original_hash
        assert verify_password("NewTestPass456!", user_after.password_hash)
        assert not verify_password("testpassword123", user_after.password_hash)
    
    async def test_admin_update_own_password(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_users: dict
    ):
        """Test admin can update their own password"""
        # Get admin user
        admin_user = test_users["admin"]
        
        # Admin updates their own password
        response = await authenticated_client.put(
            f"/api/v1/users/{admin_user.id}/password",
            json={
                "current_password": "testpassword123",
                "new_password": "NewAdminPass456!"
            }
        )
        
        assert response.status_code == 200
        
        # Verify password was changed
        updated_admin = await user_repository.get(db_session, id=admin_user.id)
        assert verify_password("NewAdminPass456!", updated_admin.password_hash)
    
    async def test_admin_reset_other_user_password(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test admin can reset another user's password without knowing current password"""
        # Create a regular user
        regular_user = await user_repository.create_with_password(
            db_session,
            obj_in=UserCreate(
                username="resetuser",
                email="reset@example.com",
                password="OriginalPass123!",
                full_name="Reset User",
                role="user"
            )
        )
        
        # Admin resets user's password without knowing current password
        response = await authenticated_client.put(
            f"/api/v1/users/{regular_user.id}/admin-reset-password",
            json={
                "new_password": "AdminResetPass456!",
                "reason": "User forgot password"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(regular_user.id)
        
        # Verify the password was actually changed
        updated_user = await user_repository.get(db_session, id=regular_user.id)
        assert verify_password("AdminResetPass456!", updated_user.password_hash)
        assert not verify_password("OriginalPass123!", updated_user.password_hash)
    
    async def test_regular_user_cannot_use_admin_reset_endpoint(
        self, 
        client: AsyncClient,
        db_session: AsyncSession,
        test_users: dict
    ):
        """Test regular user cannot use admin reset endpoint"""
        auth_headers = await create_auth_headers(test_users["user"])
        
        # Create another user to try to reset
        target_user = await user_repository.create_with_password(
            db_session,
            obj_in=UserCreate(
                username="targetuser",
                email="target@example.com",
                password="TargetPass123!",
                full_name="Target User",
                role="user"
            )
        )
        
        # Regular user tries to use admin reset endpoint
        response = await client.put(
            f"/api/v1/users/{target_user.id}/admin-reset-password",
            json={
                "new_password": "HackedPass456!",
                "reason": "Malicious attempt"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not enough permissions"
    
    async def test_admin_reset_nonexistent_user(
        self, 
        authenticated_client: AsyncClient
    ):
        """Test admin reset for non-existent user returns 404"""
        fake_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = await authenticated_client.put(
            f"/api/v1/users/{fake_user_id}/admin-reset-password",
            json={
                "new_password": "NewPassword456!",
                "reason": "Test reset"
            }
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
    
    async def test_admin_reset_with_short_password(
        self, 
        authenticated_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test admin reset fails with too short new password"""
        # Create a regular user
        regular_user = await user_repository.create_with_password(
            db_session,
            obj_in=UserCreate(
                username="shortpassuser",
                email="shortpass@example.com",
                password="OriginalPass123!",
                full_name="Short Pass User",
                role="user"
            )
        )
        
        response = await authenticated_client.put(
            f"/api/v1/users/{regular_user.id}/admin-reset-password",
            json={
                "new_password": "Short1!",  # Less than 8 characters
                "reason": "Test validation"
            }
        )
        
        assert response.status_code == 422  # Validation error