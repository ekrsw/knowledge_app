"""
Revision repository for database operations
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.article import Article
from app.schemas.revision import RevisionCreate, RevisionUpdate
from .base import BaseRepository


class RevisionRepository(BaseRepository[Revision, RevisionCreate, RevisionUpdate]):
    """Repository for revision-related database operations"""
    
    def __init__(self):
        super().__init__(Revision)
    
    async def get_by_status(
        self, 
        db: AsyncSession, 
        *, 
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by status"""
        result = await db.execute(
            select(Revision)
            .where(Revision.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_proposer(
        self, 
        db: AsyncSession, 
        *, 
        proposer_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by proposer"""
        result = await db.execute(
            select(Revision)
            .where(Revision.proposer_id == proposer_id)
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_approver(
        self, 
        db: AsyncSession, 
        *, 
        approver_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by approver"""
        result = await db.execute(
            select(Revision)
            .where(Revision.approver_id == approver_id)
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_target_article(
        self, 
        db: AsyncSession, 
        *, 
        target_article_id: str
    ) -> List[Revision]:
        """Get revisions for a specific article"""
        result = await db.execute(
            select(Revision)
            .where(Revision.target_article_id == target_article_id)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_pending_for_approver(
        self,
        db: AsyncSession,
        *,
        approver_id: UUID
    ) -> List[Revision]:
        """Get pending revisions that can be approved by a specific approver"""
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.status == "submitted",
                    Revision.approver_id == approver_id
                )
            )
            .order_by(Revision.created_at.asc())
        )
        return result.scalars().all()
    
    async def get_by_proposer_and_status(
        self,
        db: AsyncSession,
        *,
        proposer_id: UUID,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by proposer and status"""
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.proposer_id == proposer_id,
                    Revision.status == status
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def create_with_proposer(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any]
    ) -> Revision:
        """Create new revision with proposer_id"""
        db_obj = Revision(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_approver_groups(
        self,
        db: AsyncSession,
        *,
        approval_group_ids: List[UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions for articles that belong to specific approval groups"""
        # Join with articles to filter by approval group
        result = await db.execute(
            select(Revision)
            .join(Article, Revision.target_article_id == Article.article_id)
            .where(Article.approval_group.in_(approval_group_ids))
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_status_and_approver_groups(
        self,
        db: AsyncSession,
        *,
        status: str,
        approval_group_ids: List[UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by status for articles that belong to specific approval groups"""
        result = await db.execute(
            select(Revision)
            .join(Article, Revision.target_article_id == Article.article_id)
            .where(
                and_(
                    Revision.status == status,
                    Article.approval_group.in_(approval_group_ids)
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_status_and_proposer(
        self,
        db: AsyncSession,
        *,
        status: str,
        proposer_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions by status and proposer"""
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.status == status,
                    Revision.proposer_id == proposer_id
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_target_article(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID
    ) -> Optional[Article]:
        """Get the target article for a revision"""
        revision = await self.get(db, id=revision_id)
        if not revision:
            return None
        
        result = await db.execute(
            select(Article)
            .where(Article.article_id == revision.target_article_id)
        )
        return result.scalar_one_or_none()


# Create a singleton instance
revision_repository = RevisionRepository()