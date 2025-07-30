"""
Information Category repository for database operations
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.info_category import InfoCategory
from app.schemas.info_category import InfoCategoryCreate, InfoCategoryUpdate
from .base import BaseRepository


class InfoCategoryRepository(BaseRepository[InfoCategory, InfoCategoryCreate, InfoCategoryUpdate]):
    """Repository for information category-related database operations"""
    
    def __init__(self):
        super().__init__(InfoCategory)
    
    async def get_by_id(self, db: AsyncSession, *, category_id: str) -> Optional[InfoCategory]:
        """Get information category by category_id"""
        result = await db.execute(select(InfoCategory).where(InfoCategory.category_id == category_id))
        return result.scalars().first()
    
    async def get_active_categories(self, db: AsyncSession) -> List[InfoCategory]:
        """Get all active information categories ordered by display_order"""
        result = await db.execute(
            select(InfoCategory)
            .where(InfoCategory.is_active == True)
            .order_by(InfoCategory.display_order, InfoCategory.category_name)
        )
        return result.scalars().all()


# Create a singleton instance
info_category_repository = InfoCategoryRepository()