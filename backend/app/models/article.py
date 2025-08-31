"""
Article model for the Knowledge Revision System
"""
from typing import Optional, List
from datetime import date
from uuid import UUID
from sqlalchemy import String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Article(Base):
    """Article model for existing knowledge articles (reference-only)"""
    
    __tablename__ = "articles"
    
    # Primary key
    article_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    # Reference information
    article_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    article_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Approval group assignment
    approval_group: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("approval_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Article content fields
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    info_category: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("info_categories.category_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    importance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    publish_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    publish_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    target: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    approval_group_obj: Mapped[Optional["ApprovalGroup"]] = relationship("ApprovalGroup", back_populates="articles")
    info_category_obj: Mapped[Optional["InfoCategory"]] = relationship("InfoCategory", back_populates="articles")
    revisions: Mapped[List["Revision"]] = relationship("Revision", back_populates="target_article", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Article(article_id='{self.article_id}', title='{self.title}')"