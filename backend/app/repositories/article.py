"""
Article repository for database operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate
from .base import BaseRepository


class ArticleRepository(BaseRepository[Article, ArticleCreate, ArticleUpdate]):
    """Repository for article-related database operations"""
    
    def __init__(self):
        super().__init__(Article)
    
    async def get_by_id(self, db: AsyncSession, *, article_id: str) -> Optional[Article]:
        """Get article by article_id"""
        result = await db.execute(select(Article).where(Article.article_id == article_id))
        return result.scalars().first()
    
    async def get_by_number(self, db: AsyncSession, *, article_number: str) -> Optional[Article]:
        """Get article by article_number"""
        result = await db.execute(select(Article).where(Article.article_number == article_number))
        return result.scalars().first()
    
    async def get_by_approval_group(
        self, 
        db: AsyncSession, 
        *, 
        approval_group: UUID
    ) -> List[Article]:
        """Get articles by approval group"""
        result = await db.execute(
            select(Article).where(Article.approval_group == approval_group)
        )
        return result.scalars().all()
    
    async def get_by_category(
        self, 
        db: AsyncSession, 
        *, 
        info_category: UUID
    ) -> List[Article]:
        """Get articles by information category"""
        result = await db.execute(
            select(Article).where(Article.info_category == info_category)
        )
        return result.scalars().all()
    
    async def get_article_id_by_number(self, db: AsyncSession, *, article_number: str) -> Optional[str]:
        """Get article_id by article_number"""
        result = await db.execute(
            select(Article.article_id).where(Article.article_number == article_number)
        )
        article_id = result.scalars().first()
        return article_id
    
    async def get_article_number_by_id(self, db: AsyncSession, *, article_id: str) -> Optional[str]:
        """Get article_number by article_id"""
        result = await db.execute(
            select(Article.article_number).where(Article.article_id == article_id)
        )
        article_number = result.scalars().first()
        return article_number


# Create a singleton instance
article_repository = ArticleRepository()