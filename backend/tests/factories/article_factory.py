"""
Article factory for test data generation
"""
from typing import Optional
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.approval_group import ApprovalGroup
from app.models.info_category import InfoCategory


class ArticleFactory:
    """Factory for creating test articles"""
    
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
        article_id: Optional[str] = None,
        article_number: Optional[str] = None,
        article_url: Optional[str] = None,
        title: Optional[str] = None,
        info_category: Optional[InfoCategory] = None,
        approval_group: Optional[ApprovalGroup] = None,
        keywords: Optional[str] = None,
        importance: Optional[bool] = None,
        publish_start: Optional[date] = None,
        publish_end: Optional[date] = None,
        target: Optional[str] = None,
        question: Optional[str] = None,
        answer: Optional[str] = None,
        additional_comment: Optional[str] = None
    ) -> Article:
        """
        Create a test article
        
        Args:
            db: Database session
            article_id: Article ID (auto-generated if None)
            article_number: Article number (auto-generated if None)
            article_url: Article URL
            title: Article title (auto-generated if None)
            info_category: Information category to assign
            approval_group: Approval group to assign
            keywords: Keywords
            importance: Importance flag
            publish_start: Publication start date
            publish_end: Publication end date
            target: Target audience
            question: Question content
            answer: Answer content
            additional_comment: Additional comments
        
        Returns:
            Created Article object
        """
        counter = cls.get_next_counter()
        
        if article_id is None:
            article_id = f"ART-{counter:06d}"
        
        if article_number is None:
            article_number = f"KB-{counter:04d}"
        
        if title is None:
            title = f"Test Article {counter}: Knowledge Base Entry"
        
        if article_url is None:
            article_url = f"https://knowledge-base.company.com/articles/{article_id}"
        
        # Set default dates
        if publish_start is None:
            publish_start = date.today() - timedelta(days=30)
        if publish_end is None:
            publish_end = date.today() + timedelta(days=365)
        
        # Add unique suffix to avoid conflicts
        try:
            # Check if article_id exists
            from sqlalchemy import select
            result = await db.execute(
                select(Article).where(Article.article_id == article_id)
            )
            if result.scalar_one_or_none():
                article_id = f"{article_id}-{counter}"
        except:
            pass
        
        article = Article(
            article_id=article_id,
            article_number=article_number,
            article_url=article_url,
            title=title,
            info_category=info_category.category_id if info_category else None,
            approval_group=approval_group.group_id if approval_group else None,
            keywords=keywords or f"keyword{counter}, test, knowledge",
            importance=importance if importance is not None else (counter % 2 == 0),
            publish_start=publish_start,
            publish_end=publish_end,
            target=target or "All employees",
            question=question or f"What is the procedure for {title.lower()}?",
            answer=answer or f"This is the detailed answer for test article {counter}. Follow these steps...",
            additional_comment=additional_comment
        )
        
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        return article
    
    @classmethod
    async def create_tech_article(
        cls,
        db: AsyncSession,
        info_category: InfoCategory,
        approval_group: ApprovalGroup,
        **kwargs
    ) -> Article:
        """Create a technology-focused article"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            title=f"Technical Guide {counter}: System Configuration",
            info_category=info_category,
            approval_group=approval_group,
            keywords="technology, system, configuration, guide",
            importance=True,
            target="IT Staff",
            question="How do I configure the system properly?",
            answer="Follow these technical configuration steps...",
            **kwargs
        )
    
    @classmethod
    async def create_business_article(
        cls,
        db: AsyncSession,
        info_category: InfoCategory,
        approval_group: ApprovalGroup,
        **kwargs
    ) -> Article:
        """Create a business-focused article"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            title=f"Business Process {counter}: Workflow Guidelines",
            info_category=info_category,
            approval_group=approval_group,
            keywords="business, process, workflow, guidelines",
            importance=False,
            target="Business Users",
            question="What is the correct business workflow?",
            answer="The business workflow follows these guidelines...",
            **kwargs
        )
    
    @classmethod
    async def create_important_article(
        cls,
        db: AsyncSession,
        info_category: InfoCategory,
        approval_group: ApprovalGroup,
        **kwargs
    ) -> Article:
        """Create an important high-priority article"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            title=f"CRITICAL: Security Policy {counter}",
            info_category=info_category,
            approval_group=approval_group,
            keywords="critical, security, policy, important",
            importance=True,
            target="All Staff",
            question="What are the security requirements?",
            answer="CRITICAL security requirements include...",
            **kwargs
        )
    
    @classmethod
    async def create_expired_article(
        cls,
        db: AsyncSession,
        info_category: InfoCategory,
        approval_group: ApprovalGroup,
        **kwargs
    ) -> Article:
        """Create an article with expired publication dates"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            title=f"Expired Article {counter}: Legacy Process",
            info_category=info_category,
            approval_group=approval_group,
            keywords="expired, legacy, deprecated",
            importance=False,
            publish_start=date.today() - timedelta(days=365),
            publish_end=date.today() - timedelta(days=30),
            **kwargs
        )
    
    @classmethod
    async def create_with_minimal_category(
        cls,
        db: AsyncSession,
        approval_group: ApprovalGroup,
        **kwargs
    ) -> Article:
        """Create an article with minimal info category setup"""
        from .info_category_factory import InfoCategoryFactory
        
        # Create a minimal info category
        info_category = await InfoCategoryFactory.create(
            db=db,
            category_name="Minimal Category",
            display_order=1,
            is_active=True
        )
        
        return await cls.create(
            db=db,
            info_category=info_category,
            approval_group=approval_group,
            **kwargs
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        info_category: Optional[InfoCategory] = None,
        approval_group: Optional[ApprovalGroup] = None,
        **kwargs
    ) -> list[Article]:
        """Create multiple articles at once"""
        articles = []
        for i in range(count):
            article = await cls.create(
                db=db,
                info_category=info_category,
                approval_group=approval_group,
                **kwargs
            )
            articles.append(article)
        
        return articles