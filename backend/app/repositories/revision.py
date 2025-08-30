"""
Revision repository for database operations
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.article import Article
from app.models.user import User
from app.schemas.revision import RevisionCreate, RevisionUpdate
from .base import BaseRepository


class RevisionRepository(BaseRepository[Revision, RevisionCreate, RevisionUpdate]):
    """Repository for revision-related database operations"""
    
    def __init__(self):
        super().__init__(Revision)
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[Revision]:
        """Get a single revision by ID - override to use revision_id"""
        result = await db.execute(
            select(Revision).where(Revision.revision_id == id)
        )
        return result.scalars().first()
    
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
    
    async def get_public_revisions(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get publicly accessible revisions (submitted and approved)"""
        result = await db.execute(
            select(Revision)
            .where(Revision.status.in_(["submitted", "approved"]))
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_user_private_revisions(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get user's private revisions (draft and rejected)"""
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.proposer_id == user_id,
                    Revision.status.in_(["draft", "rejected"])
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_mixed_access_revisions(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get revisions with mixed access control - public + user's private + approver's rejected"""
        result = await db.execute(
            select(Revision)
            .where(
                or_(
                    # Public revisions (submitted/approved)
                    Revision.status.in_(["submitted", "approved"]),
                    # User's private revisions (draft/rejected as proposer)
                    and_(
                        Revision.proposer_id == user_id,
                        Revision.status.in_(["draft", "rejected"])
                    ),
                    # Approver can see rejected revisions they were assigned to approve
                    and_(
                        Revision.approver_id == user_id,
                        Revision.status == "rejected"
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_public_revisions_by_article(
        self,
        db: AsyncSession,
        *,
        target_article_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get public revisions (submitted/approved) for a specific article"""
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.target_article_id == target_article_id,
                    Revision.status.in_(["submitted", "approved"])
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_with_names(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all revisions with proposer and approver names, and article number"""
        # Create aliases for proposer and approver
        proposer = aliased(User)
        approver = aliased(User)
        
        result = await db.execute(
            select(
                Revision,
                proposer.full_name.label("proposer_name"),
                approver.full_name.label("approver_name"),
                Article.article_number
            )
            .join(proposer, Revision.proposer_id == proposer.id)
            .outerjoin(approver, Revision.approver_id == approver.id)
            .outerjoin(Article, Revision.target_article_id == Article.article_id)
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        
        revisions_with_names = []
        for row in result:
            revision_dict = {
                "revision_id": row.Revision.revision_id,
                "article_number": row.article_number,  # Use article_number instead of target_article_id
                "reason": row.Revision.reason,
                "after_title": row.Revision.after_title,
                "after_info_category": row.Revision.after_info_category,
                "after_keywords": row.Revision.after_keywords,
                "after_importance": row.Revision.after_importance,
                "after_publish_start": row.Revision.after_publish_start,
                "after_publish_end": row.Revision.after_publish_end,
                "after_target": row.Revision.after_target,
                "after_question": row.Revision.after_question,
                "after_answer": row.Revision.after_answer,
                "after_additional_comment": row.Revision.after_additional_comment,
                "status": row.Revision.status,
                "processed_at": row.Revision.processed_at,
                "created_at": row.Revision.created_at,
                "updated_at": row.Revision.updated_at,
                "proposer_name": row.proposer_name,
                "approver_name": row.approver_name
            }
            revisions_with_names.append(revision_dict)
        
        return revisions_with_names
    
    async def get_mixed_access_with_names(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get revisions with mixed access control, user names, and article number"""
        # Create aliases for proposer and approver
        proposer = aliased(User)
        approver = aliased(User)
        
        result = await db.execute(
            select(
                Revision,
                proposer.full_name.label("proposer_name"),
                approver.full_name.label("approver_name"),
                Article.article_number
            )
            .join(proposer, Revision.proposer_id == proposer.id)
            .outerjoin(approver, Revision.approver_id == approver.id)
            .outerjoin(Article, Revision.target_article_id == Article.article_id)
            .where(
                or_(
                    # Public revisions (submitted/approved)
                    Revision.status.in_(["submitted", "approved"]),
                    # User's private revisions (draft/rejected as proposer)
                    and_(
                        Revision.proposer_id == user_id,
                        Revision.status.in_(["draft", "rejected"])
                    ),
                    # Approver can see rejected revisions they were assigned to approve
                    and_(
                        Revision.approver_id == user_id,
                        Revision.status == "rejected"
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        
        revisions_with_names = []
        for row in result:
            revision_dict = {
                "revision_id": row.Revision.revision_id,
                "article_number": row.article_number,  # Use article_number instead of target_article_id
                "reason": row.Revision.reason,
                "after_title": row.Revision.after_title,
                "after_info_category": row.Revision.after_info_category,
                "after_keywords": row.Revision.after_keywords,
                "after_importance": row.Revision.after_importance,
                "after_publish_start": row.Revision.after_publish_start,
                "after_publish_end": row.Revision.after_publish_end,
                "after_target": row.Revision.after_target,
                "after_question": row.Revision.after_question,
                "after_answer": row.Revision.after_answer,
                "after_additional_comment": row.Revision.after_additional_comment,
                "status": row.Revision.status,
                "processed_at": row.Revision.processed_at,
                "created_at": row.Revision.created_at,
                "updated_at": row.Revision.updated_at,
                "proposer_name": row.proposer_name,
                "approver_name": row.approver_name
            }
            revisions_with_names.append(revision_dict)
        
        return revisions_with_names


# Create a singleton instance
revision_repository = RevisionRepository()