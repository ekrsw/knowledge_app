"""
Information Category model for the Knowledge Revision System
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class InfoCategory(Base):
    """Information category model for categorizing knowledge articles"""
    
    __tablename__ = "info_categories"
    
    # Primary key
    category_id = Column(String(50), primary_key=True)
    
    # Category information
    category_name = Column(String(100), nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="info_category_obj")
    revisions = relationship("Revision", back_populates="after_info_category_obj")
    
    def __repr__(self) -> str:
        return f"<InfoCategory(category_id='{self.category_id}', name='{self.category_name}')>"