"""
Approval Group Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ApprovalGroupBase(BaseModel):
    """Base approval group schema"""
    group_id: str = Field(..., min_length=1, max_length=50)
    group_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class ApprovalGroupCreate(ApprovalGroupBase):
    """Schema for creating approval groups"""
    pass


class ApprovalGroupUpdate(BaseModel):
    """Schema for updating approval groups"""
    group_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ApprovalGroup(ApprovalGroupBase):
    """Schema for approval group response"""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True