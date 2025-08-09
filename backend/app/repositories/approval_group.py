"""
Approval Group repository for database operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_group import ApprovalGroup
from app.schemas.approval_group import ApprovalGroupCreate, ApprovalGroupUpdate
from .base import BaseRepository


class ApprovalGroupRepository(BaseRepository[ApprovalGroup, ApprovalGroupCreate, ApprovalGroupUpdate]):
    """Repository for approval group-related database operations"""
    
    def __init__(self):
        super().__init__(ApprovalGroup)
    
    async def get_by_id(self, db: AsyncSession, *, group_id: UUID) -> Optional[ApprovalGroup]:
        """Get approval group by group_id"""
        result = await db.execute(select(ApprovalGroup).where(ApprovalGroup.group_id == group_id))
        return result.scalars().first()
    
    async def get_active_groups(self, db: AsyncSession) -> List[ApprovalGroup]:
        """Get all active approval groups"""
        result = await db.execute(
            select(ApprovalGroup)
            .where(ApprovalGroup.is_active == True)
            .order_by(ApprovalGroup.group_name)
        )
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, group_name: str) -> Optional[ApprovalGroup]:
        """Get approval group by group name"""
        result = await db.execute(
            select(ApprovalGroup)
            .where(ApprovalGroup.group_name == group_name)
        )
        return result.scalars().first()
    
    async def remove(self, db: AsyncSession, *, id: UUID) -> Optional[ApprovalGroup]:
        """Delete approval group by ID (overrides base method to use group_id)"""
        result = await db.execute(
            select(ApprovalGroup).where(ApprovalGroup.group_id == id)
        )
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj


# Create a singleton instance
approval_group_repository = ApprovalGroupRepository()