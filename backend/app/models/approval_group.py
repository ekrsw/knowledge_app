"""
Approval Group model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class ApprovalGroup(Base):
    """Approval group model for organizing approval responsibilities"""
    
    __tablename__ = "approval_groups"
    
    # Primary key
    group_id = Column(String(50), primary_key=True)
    
    # Group information
    group_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    members = relationship("User", back_populates="approval_group")
    articles = relationship("Article", back_populates="approval_group")
    
    def __repr__(self) -> str:
        return f"<ApprovalGroup(group_id='{self.group_id}', name='{self.group_name}')>"