"""
Revision model for the Knowledge Revision System
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class Revision(Base):
    """Revision model for knowledge article revision proposals"""
    
    __tablename__ = "revisions"
    
    # Primary key
    revision_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Target article information
    target_article_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Not FK to allow flexibility
    
    # Proposer information
    proposer_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Revision content (after-only fields, all nullable)
    after_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_info_category: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("info_categories.category_id", ondelete="SET NULL"),
        nullable=True
    )
    after_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_importance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    after_publish_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    after_publish_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    after_target: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    after_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    after_additional_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Revision metadata
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="draft",
        server_default="draft",
        index=True
    )
    
    # Approval information
    approver_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    proposer: Mapped["User"] = relationship("User", back_populates="submitted_revisions", foreign_keys=[proposer_id])
    approver: Mapped[Optional["User"]] = relationship("User", back_populates="approved_revisions", foreign_keys=[approver_id])
    after_info_category_obj: Mapped[Optional["InfoCategory"]] = relationship("InfoCategory", back_populates="revisions")
    # Note: Since target_article_id is not a foreign key (for flexibility),
    # we don't define a relationship here. Use repository methods to fetch related articles.
    notifications: Mapped[List["SimpleNotification"]] = relationship("SimpleNotification", back_populates="revision", cascade="all, delete-orphan")
    
    # Table indexes
    __table_args__ = (
        Index('idx_revision_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Revision(revision_id={self.revision_id}, status='{self.status}', target='{self.target_article_id}')"