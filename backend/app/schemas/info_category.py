"""
Information Category Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class InfoCategoryBase(BaseModel):
    """Base information category schema"""
    category_name: str = Field(..., min_length=1, max_length=100)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class InfoCategoryCreate(InfoCategoryBase):
    """Schema for creating information categories"""
    # category_id is auto-generated UUID, not provided in create


class InfoCategoryUpdate(BaseModel):
    """Schema for updating information categories"""
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class InfoCategory(InfoCategoryBase):
    """Schema for information category response"""
    category_id: UUID  # UUID field for response
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True