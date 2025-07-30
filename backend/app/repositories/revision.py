"""
Revision repository for database operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
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


# Create a singleton instance
revision_repository = RevisionRepository()