"""
Article model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class Article(Base):
    """Article model for existing knowledge articles (reference-only)"""
    
    __tablename__ = "articles"
    
    # Primary key
    article_id = Column(String(100), primary_key=True)
    
    # Reference information
    article_pk = Column(String(200), nullable=False, index=True)
    article_number = Column(String(100), nullable=False, index=True)
    article_url = Column(Text, nullable=True)
    
    # Approval group assignment
    approval_group = Column(
        String(50), 
        ForeignKey("approval_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Article content fields
    title = Column(Text, nullable=True)
    info_category = Column(
        String(50), 
        ForeignKey("info_categories.category_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    keywords = Column(Text, nullable=True)
    importance = Column(Boolean, nullable=True)
    publish_start = Column(DateTime(timezone=True), nullable=True)
    publish_end = Column(DateTime(timezone=True), nullable=True)
    target = Column(String(100), nullable=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    additional_comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    approval_group_obj = relationship("ApprovalGroup", back_populates="articles")
    info_category_obj = relationship("InfoCategory", back_populates="articles")
    # Note: revisions relationship is handled from Revision model side only to avoid circular reference issues
    
    def __repr__(self) -> str:
        return f"<Article(article_id='{self.article_id}', title='{self.title}')>"