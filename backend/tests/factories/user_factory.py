"""
User factory for test data generation
"""
import asyncio
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.models.approval_group import ApprovalGroup

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserFactory:
    """Factory for creating test users"""
    
    _counter = 0
    
    @classmethod
    def get_next_counter(cls) -> int:
        """Get next counter value for unique identifiers"""
        cls._counter += 1
        return cls._counter
    
    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "testpassword123",
        full_name: Optional[str] = None,
        role: str = "user",
        approval_group: Optional[ApprovalGroup] = None,
        is_active: bool = True,
        sweet_name: Optional[str] = None,
        ctstage_name: Optional[str] = None
    ) -> User:
        """
        Create a test user
        
        Args:
            db: Database session
            username: Username (auto-generated if None)
            email: Email address (auto-generated if None)
            password: Password to hash
            full_name: Full name (auto-generated if None)
            role: User role (user, approver, admin)
            approval_group: Approval group to assign
            is_active: Whether user is active
            sweet_name: Sweet name identifier
            ctstage_name: CTStage name identifier
        
        Returns:
            Created User object
        """
        counter = cls.get_next_counter()
        
        if username is None:
            username = f"testuser{counter}"
        if email is None:
            email = f"testuser{counter}@example.com"
        if full_name is None:
            full_name = f"Test User {counter}"
        
        # Add unique suffix to avoid conflicts with existing users
        try:
            # Check if username exists
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                username = f"{username}_{counter}"
                email = f"testuser{counter}_{counter}@example.com"
        except:
            pass
        
        # Hash password
        password_hash = pwd_context.hash(password)
        
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            approval_group_id=approval_group.group_id if approval_group else None,
            is_active=is_active,
            sweet_name=sweet_name,
            ctstage_name=ctstage_name
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @classmethod
    async def create_admin(
        cls, 
        db: AsyncSession, 
        username: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create an admin user"""
        if username is None:
            counter = cls.get_next_counter()
            username = f"admin{counter}"
        
        return await cls.create(
            db=db,
            username=username,
            role="admin",
            **kwargs
        )
    
    @classmethod
    async def create_approver(
        cls, 
        db: AsyncSession,
        approval_group: ApprovalGroup,
        username: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create an approver user with approval group"""
        if username is None:
            counter = cls.get_next_counter()
            username = f"approver{counter}"
        
        return await cls.create(
            db=db,
            username=username,
            role="approver",
            approval_group=approval_group,
            **kwargs
        )
    
    @classmethod
    async def create_user(
        cls, 
        db: AsyncSession, 
        username: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create a regular user"""
        if username is None:
            counter = cls.get_next_counter()
            username = f"user{counter}"
        
        return await cls.create(
            db=db,
            username=username,
            role="user",
            **kwargs
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        role: str = "user",
        approval_group: Optional[ApprovalGroup] = None,
        **kwargs
    ) -> list[User]:
        """Create multiple users at once"""
        users = []
        for i in range(count):
            counter = cls.get_next_counter()
            user = await cls.create(
                db=db,
                username=f"{role}{counter}",
                role=role,
                approval_group=approval_group,
                **kwargs
            )
            users.append(user)
        
        return users