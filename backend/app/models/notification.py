"""
Notification model for the Knowledge Revision System
"""
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class SimpleNotification(Base):
    """Simple notification model for basic notification system"""
    
    __tablename__ = "simple_notifications"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # User information
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Notification content
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Related entity (optional)
    revision_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("revisions.revision_id", ondelete="CASCADE"),
        nullable=True
    )
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    revision: Mapped[Optional["Revision"]] = relationship("Revision", back_populates="notifications")
    
    # Table indexes
    __table_args__ = (
        Index('idx_notification_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SimpleNotification(id={self.id}, type='{self.type}', read={self.is_read}')"