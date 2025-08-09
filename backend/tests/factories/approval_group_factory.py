"""
Approval Group factory for test data generation
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_group import ApprovalGroup


class ApprovalGroupFactory:
    """Factory for creating test approval groups"""
    
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
        group_name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> ApprovalGroup:
        """
        Create a test approval group
        
        Args:
            db: Database session
            group_name: Group name (auto-generated if None)
            description: Group description
            is_active: Whether group is active
        
        Returns:
            Created ApprovalGroup object
        """
        counter = cls.get_next_counter()
        
        if group_name is None:
            group_name = f"Test Group {counter}"
        
        if description is None:
            description = f"Test approval group {counter} for testing purposes"
        
        # Add unique suffix to avoid conflicts
        try:
            # Check if group name exists
            from sqlalchemy import select
            result = await db.execute(
                select(ApprovalGroup).where(ApprovalGroup.group_name == group_name)
            )
            if result.scalar_one_or_none():
                group_name = f"{group_name} {counter}"
        except:
            pass
        
        approval_group = ApprovalGroup(
            group_name=group_name,
            description=description,
            is_active=is_active
        )
        
        db.add(approval_group)
        await db.commit()
        await db.refresh(approval_group)
        
        return approval_group
    
    @classmethod
    async def create_development_group(cls, db: AsyncSession) -> ApprovalGroup:
        """Create a development team approval group"""
        # Check if already exists first
        from sqlalchemy import select
        try:
            result = await db.execute(
                select(ApprovalGroup).where(ApprovalGroup.group_name == "Development Team")
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing
        except:
            pass
            
        return await cls.create(
            db=db,
            group_name="Development Team",
            description="Approval group for development-related knowledge articles"
        )
    
    @classmethod
    async def create_quality_group(cls, db: AsyncSession) -> ApprovalGroup:
        """Create a quality assurance approval group"""
        # Check if already exists first
        from sqlalchemy import select
        try:
            result = await db.execute(
                select(ApprovalGroup).where(ApprovalGroup.group_name == "Quality Assurance")
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing
        except:
            pass
            
        return await cls.create(
            db=db,
            group_name="Quality Assurance",
            description="Approval group for QA and testing-related articles"
        )
    
    @classmethod
    async def create_management_group(cls, db: AsyncSession) -> ApprovalGroup:
        """Create a management approval group"""
        # Check if already exists first
        from sqlalchemy import select
        try:
            result = await db.execute(
                select(ApprovalGroup).where(ApprovalGroup.group_name == "Management Team")
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing
        except:
            pass
            
        return await cls.create(
            db=db,
            group_name="Management Team",
            description="Approval group for management and policy articles"
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        base_name: str = "Test Group",
        **kwargs
    ) -> list[ApprovalGroup]:
        """Create multiple approval groups at once"""
        groups = []
        for i in range(count):
            counter = cls.get_next_counter()
            group = await cls.create(
                db=db,
                group_name=f"{base_name} {counter}",
                **kwargs
            )
            groups.append(group)
        
        return groups