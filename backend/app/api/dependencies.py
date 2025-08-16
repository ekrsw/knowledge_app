"""
API dependencies for dependency injection
"""
from typing import AsyncGenerator
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.core.security import verify_token
from app.repositories.user import user_repository
from app.models.user import User

# JWT Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if credentials are provided
    if credentials is None:
        raise credentials_exception
    
    # Verify token
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    try:
        user_uuid = UUID(user_id)
        user = await user_repository.get(db, id=user_uuid)
        if user is None:
            raise credentials_exception
        return user
    except ValueError:
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


async def get_current_approver_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user with approver or admin role"""
    if current_user.role not in ["approver", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user with admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user