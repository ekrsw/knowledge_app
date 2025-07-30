"""
Notification model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from . import Base


class SimpleNotification(Base):
    """Simple notification model for basic notification system"""
    
    __tablename__ = "simple_notifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Notification content
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, index=True)
    
    # Related entity (optional)
    revision_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("revisions.revision_id", ondelete="CASCADE"),
        nullable=True
    )
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    revision = relationship("Revision", back_populates="notifications")
    
    def __repr__(self) -> str:
        return f"<SimpleNotification(id={self.id}, type='{self.type}', read={self.is_read})>"