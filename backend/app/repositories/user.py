"""
User repository for database operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for user-related database operations"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()
    
    async def get_by_approval_group(
        self, 
        db: AsyncSession, 
        *, 
        approval_group_id: UUID
    ) -> List[User]:
        """Get users by approval group"""
        result = await db.execute(
            select(User).where(User.approval_group_id == approval_group_id)
        )
        return result.scalars().all()
    
    async def get_active_users(self, db: AsyncSession) -> List[User]:
        """Get all active users"""
        result = await db.execute(select(User).where(User.is_active == True))
        return result.scalars().all()
    
    async def get_by_role(self, db: AsyncSession, *, role: str) -> List[User]:
        """Get users by role"""
        result = await db.execute(select(User).where(User.role == role))
        return result.scalars().all()
    
    async def authenticate(self, db: AsyncSession, *, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        from app.core.security import verify_password
        
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    async def create_with_password(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        from app.core.security import get_password_hash
        
        # Hash the password
        hashed_password = get_password_hash(obj_in.password)
        
        # Create user data without password
        user_data = obj_in.model_dump(exclude={"password"})
        user_data["password_hash"] = hashed_password
        
        # Create user object
        db_obj = User(**user_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Create a singleton instance
user_repository = UserRepository()