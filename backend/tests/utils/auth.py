"""
Authentication utilities for tests
"""
from typing import Dict, Any
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.core.security import create_access_token
from app.models.user import User


async def get_auth_token(user: User) -> str:
    """
    Generate JWT token for a test user
    
    Args:
        user: User object to generate token for
    
    Returns:
        JWT access token string
    """
    return create_access_token(subject=str(user.id), role=user.role)


async def create_auth_headers(user: User) -> Dict[str, str]:
    """
    Create authentication headers for a test user
    
    Args:
        user: User object to create headers for
    
    Returns:
        Dictionary with Authorization header
    """
    token = await get_auth_token(user)
    return {"Authorization": f"Bearer {token}"}


async def create_authenticated_client(client: AsyncClient, user: User) -> AsyncClient:
    """
    Create an authenticated HTTP client
    
    Args:
        client: Base AsyncClient
        user: User to authenticate as
    
    Returns:
        AsyncClient with authentication headers set
    """
    headers = await create_auth_headers(user)
    client.headers.update(headers)
    return client


async def create_expired_token() -> str:
    """
    Create an expired JWT token for testing
    
    Returns:
        Expired JWT token string
    """
    # Create token that expired 1 hour ago
    from uuid import uuid4
    return create_access_token(subject=str(uuid4()), expires_delta=timedelta(hours=-1), role="user")


def create_invalid_token() -> str:
    """
    Create an invalid JWT token for testing
    
    Returns:
        Invalid JWT token string
    """
    return "invalid.jwt.token"


async def login_user(client: AsyncClient, username: str, password: str) -> Dict[str, Any]:
    """
    Login a user and return the response
    
    Args:
        client: AsyncClient for making requests
        username: Username to login with
        password: Password to login with
    
    Returns:
        Login response data
    """
    login_data = {
        "username": username,
        "password": password
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    return response.json()


async def create_test_user_and_token(db, role: str = "user", approval_group=None, **kwargs) -> tuple[User, str]:
    """
    Create a test user and generate authentication token
    
    Args:
        db: Database session
        role: User role (user, approver, admin)
        approval_group: ApprovalGroup object (required for approver role)
        **kwargs: Additional user creation parameters
    
    Returns:
        Tuple of (User object, JWT token)
    """
    from tests.factories.user_factory import UserFactory
    
    if role == "admin":
        user = await UserFactory.create_admin(db, **kwargs)
    elif role == "approver":
        if approval_group is None:
            # Create a default approval group for approver
            from tests.factories.approval_group_factory import ApprovalGroupFactory
            approval_group = await ApprovalGroupFactory.create_development_group(db)
        user = await UserFactory.create_approver(db, approval_group, **kwargs)
    else:
        user = await UserFactory.create_user(db, **kwargs)
    
    token = await get_auth_token(user)
    return user, token