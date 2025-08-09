"""
Revision factory for test data generation
"""
from typing import Optional
from uuid import UUID
from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.user import User
from app.models.info_category import InfoCategory


class RevisionFactory:
    """Factory for creating test revisions"""
    
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
        target_article_id: Optional[str] = None,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        status: str = "draft",
        reason: Optional[str] = None,
        after_title: Optional[str] = None,
        after_info_category: Optional[InfoCategory] = None,
        after_keywords: Optional[str] = None,
        after_importance: Optional[bool] = None,
        after_publish_start: Optional[date] = None,
        after_publish_end: Optional[date] = None,
        after_target: Optional[str] = None,
        after_question: Optional[str] = None,
        after_answer: Optional[str] = None,
        after_additional_comment: Optional[str] = None,
        processed_at: Optional[datetime] = None,
    ) -> Revision:
        """
        Create a test revision
        
        Args:
            db: Database session
            target_article_id: Target article ID
            proposer: Proposer user (created if None)
            approver: Approver user (created if None)
            status: Revision status
            reason: Reason for revision
            after_*: After-only fields for revision content
            processed_at: Processing timestamp
        
        Returns:
            Created Revision object
        """
        counter = cls.get_next_counter()
        
        # Create default users if not provided
        if proposer is None:
            from .user_factory import UserFactory
            proposer = await UserFactory.create_user(
                db=db,
                username=f"testproposer{counter}"
            )
        
        if approver is None:
            from .user_factory import UserFactory
            from .approval_group_factory import ApprovalGroupFactory
            
            # Create approval group for the approver
            approval_group = await ApprovalGroupFactory.create_development_group(db)
            approver = await UserFactory.create_approver(
                db=db,
                approval_group=approval_group,
                username=f"testapprover{counter}"
            )
        
        # Set default values
        if target_article_id is None:
            target_article_id = f"test-article-{counter}"
        
        if reason is None:
            reason = f"Test revision reason {counter}"
        
        revision = Revision(
            target_article_id=target_article_id,
            proposer_id=proposer.id,
            approver_id=approver.id,
            status=status,
            reason=reason,
            after_title=after_title,
            after_info_category=after_info_category.category_id if after_info_category else None,
            after_keywords=after_keywords,
            after_importance=after_importance,
            after_publish_start=after_publish_start,
            after_publish_end=after_publish_end,
            after_target=after_target,
            after_question=after_question,
            after_answer=after_answer,
            after_additional_comment=after_additional_comment,
            processed_at=processed_at,
        )
        
        db.add(revision)
        await db.commit()
        await db.refresh(revision)
        
        return revision
    
    @classmethod
    async def create_draft(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create a draft revision"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            status="draft",
            proposer=proposer,
            approver=approver,
            reason=f"Draft revision {counter}",
            **kwargs
        )
    
    @classmethod
    async def create_submitted(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create a submitted revision"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            status="submitted",
            proposer=proposer,
            approver=approver,
            reason=f"Submitted revision {counter}",
            **kwargs
        )
    
    @classmethod
    async def create_approved(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create an approved revision"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            status="approved",
            proposer=proposer,
            approver=approver,
            reason=f"Approved revision {counter}",
            processed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    async def create_rejected(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create a rejected revision"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            status="rejected",
            proposer=proposer,
            approver=approver,
            reason=f"Rejected revision {counter}",
            processed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    async def create_deleted(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create a deleted revision"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            status="deleted",
            proposer=proposer,
            approver=approver,
            reason=f"Deleted revision {counter}",
            processed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    async def create_with_content(
        cls,
        db: AsyncSession,
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> Revision:
        """Create a revision with sample content"""
        counter = cls.get_next_counter()
        
        from .info_category_factory import InfoCategoryFactory
        
        # Create info category if not provided
        if "after_info_category" not in kwargs:
            info_category = await InfoCategoryFactory.create_business_category(db)
            kwargs["after_info_category"] = info_category
        
        return await cls.create(
            db=db,
            proposer=proposer,
            approver=approver,
            after_title=f"Test Article Title {counter}",
            after_keywords=f"test, keywords, {counter}",
            after_importance=True,
            after_publish_start=date(2024, 1, 1),
            after_publish_end=date(2024, 12, 31),
            after_target="テスト対象者",
            after_question=f"Test question {counter}?",
            after_answer=f"Test answer {counter}.",
            after_additional_comment=f"Additional test comment {counter}.",
            **kwargs
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        status: str = "draft",
        proposer: Optional[User] = None,
        approver: Optional[User] = None,
        **kwargs
    ) -> list[Revision]:
        """Create multiple revisions at once"""
        revisions = []
        for i in range(count):
            revision = await cls.create(
                db=db,
                status=status,
                proposer=proposer,
                approver=approver,
                **kwargs
            )
            revisions.append(revision)
        
        return revisions