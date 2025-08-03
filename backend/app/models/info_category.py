"""
Information Category model for the Knowledge Revision System
"""
from typing import List
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class InfoCategory(Base):
    """Information category model for categorizing knowledge articles"""
    
    __tablename__ = "info_categories"
    
    # Primary key
    category_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Category information
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    articles: Mapped[List["Article"]] = relationship("Article", back_populates="info_category_obj")
    revisions: Mapped[List["Revision"]] = relationship("Revision", back_populates="after_info_category_obj")
    
    def __repr__(self) -> str:
        return f"<InfoCategory(category_id={self.category_id}, name='{self.category_name}')"