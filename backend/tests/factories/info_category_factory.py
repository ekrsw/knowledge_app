"""
Information Category factory for test data generation
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.info_category import InfoCategory


class InfoCategoryFactory:
    """Factory for creating test information categories"""
    
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
        category_name: Optional[str] = None,
        display_order: Optional[int] = None,
        is_active: bool = True
    ) -> InfoCategory:
        """
        Create a test information category
        
        Args:
            db: Database session
            category_name: Category name (auto-generated if None)
            display_order: Display order (auto-generated if None)
            is_active: Whether category is active
        
        Returns:
            Created InfoCategory object
        """
        counter = cls.get_next_counter()
        
        if category_name is None:
            category_name = f"Test Category {counter}"
        
        if display_order is None:
            display_order = counter * 10
        
        # Add unique suffix to avoid conflicts
        try:
            # Check if category name exists
            from sqlalchemy import select
            result = await db.execute(
                select(InfoCategory).where(InfoCategory.category_name == category_name)
            )
            if result.scalar_one_or_none():
                category_name = f"{category_name} {counter}"
        except:
            pass
        
        info_category = InfoCategory(
            category_name=category_name,
            display_order=display_order,
            is_active=is_active
        )
        
        db.add(info_category)
        await db.commit()
        await db.refresh(info_category)
        
        return info_category
    
    @classmethod
    async def create_technology_category(cls, db: AsyncSession) -> InfoCategory:
        """Create a technology information category"""
        return await cls.create(
            db=db,
            category_name="Technology",
            display_order=10
        )
    
    @classmethod
    async def create_business_category(cls, db: AsyncSession) -> InfoCategory:
        """Create a business information category"""
        return await cls.create(
            db=db,
            category_name="Business",
            display_order=20
        )
    
    @classmethod
    async def create_operations_category(cls, db: AsyncSession) -> InfoCategory:
        """Create an operations information category"""
        return await cls.create(
            db=db,
            category_name="Operations",
            display_order=30
        )
    
    @classmethod
    async def create_compliance_category(cls, db: AsyncSession) -> InfoCategory:
        """Create a compliance information category"""
        return await cls.create(
            db=db,
            category_name="Compliance",
            display_order=40
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        base_name: str = "Test Category",
        **kwargs
    ) -> list[InfoCategory]:
        """Create multiple information categories at once"""
        categories = []
        for i in range(count):
            counter = cls.get_next_counter()
            category = await cls.create(
                db=db,
                category_name=f"{base_name} {counter}",
                display_order=counter * 10,
                **kwargs
            )
            categories.append(category)
        
        return categories