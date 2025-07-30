"""
User model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from . import Base


class User(Base):
    """User model with approval group membership"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic user information
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    
    # Additional identifiers
    sweet_name = Column(String(50), unique=True, nullable=True, index=True)
    ctstage_name = Column(String(50), unique=True, nullable=True, index=True)
    
    # Role and approval group
    role = Column(
        String(20), 
        nullable=False, 
        default="user",
        server_default="user"
    )
    approval_group_id = Column(
        String(50), 
        ForeignKey("approval_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    approval_group = relationship("ApprovalGroup", back_populates="members")
    submitted_revisions = relationship("Revision", back_populates="proposer", foreign_keys="[Revision.proposer_id]")
    approved_revisions = relationship("Revision", back_populates="approver", foreign_keys="[Revision.approver_id]")
    notifications = relationship("SimpleNotification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"