"""
User model for the Knowledge Revision System
"""
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class User(Base):
    """User model with approval group membership"""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Basic user information
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Additional identifiers
    sweet_name: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    ctstage_name: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    
    # Role and approval group
    role: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="user",
        server_default="user"
    )
    approval_group_id: Mapped[Optional[str]] = mapped_column(
        String(50), 
        ForeignKey("approval_groups.group_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    approval_group: Mapped[Optional["ApprovalGroup"]] = relationship("ApprovalGroup", back_populates="members")
    submitted_revisions: Mapped[List["Revision"]] = relationship("Revision", back_populates="proposer", foreign_keys="[Revision.proposer_id]")
    approved_revisions: Mapped[List["Revision"]] = relationship("Revision", back_populates="approver", foreign_keys="[Revision.approver_id]")
    notifications: Mapped[List["SimpleNotification"]] = relationship("SimpleNotification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')"