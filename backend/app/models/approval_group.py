"""
Approval Group model for the Knowledge Revision System
"""
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class ApprovalGroup(Base):
    """Approval group model for organizing approval responsibilities"""
    
    __tablename__ = "approval_groups"
    
    # Primary key
    group_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Group information
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    members: Mapped[List["User"]] = relationship("User", back_populates="approval_group")
    articles: Mapped[List["Article"]] = relationship("Article", back_populates="approval_group_obj")
    
    def __repr__(self) -> str:
        return f"<ApprovalGroup(group_id='{self.group_id}', name='{self.group_name}')"