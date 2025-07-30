"""
Revision model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from . import Base


class Revision(Base):
    """Revision model for knowledge article revision proposals"""
    
    __tablename__ = "revisions"
    
    # Primary key
    revision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Target article information
    target_article_id = Column(String(100), nullable=False, index=True)  # Not FK to allow flexibility
    target_article_pk = Column(String(200), nullable=False)
    
    # Proposer information
    proposer_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Revision content (after-only fields, all nullable)
    after_title = Column(Text, nullable=True)
    after_info_category = Column(
        String(50), 
        ForeignKey("info_categories.category_id", ondelete="SET NULL"),
        nullable=True
    )
    after_keywords = Column(Text, nullable=True)
    after_importance = Column(Boolean, nullable=True)
    after_publish_start = Column(DateTime(timezone=True), nullable=True)
    after_publish_end = Column(DateTime(timezone=True), nullable=True)
    after_target = Column(String(100), nullable=True)
    after_question = Column(Text, nullable=True)
    after_answer = Column(Text, nullable=True)
    after_additional_comment = Column(Text, nullable=True)
    
    # Revision metadata
    reason = Column(Text, nullable=False)
    status = Column(
        String(20), 
        nullable=False, 
        default="draft",
        server_default="draft",
        index=True
    )
    
    # Approval information
    approver_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    proposer = relationship("User", back_populates="submitted_revisions", foreign_keys=[proposer_id])
    approver = relationship("User", back_populates="approved_revisions", foreign_keys=[approver_id])
    after_info_category_obj = relationship("InfoCategory", back_populates="revisions")
    target_article = relationship("Article", back_populates="revisions")
    notifications = relationship("SimpleNotification", back_populates="revision", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Revision(revision_id={self.revision_id}, status='{self.status}', target='{self.target_article_id}')>"