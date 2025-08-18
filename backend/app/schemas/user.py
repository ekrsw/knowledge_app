"""
User Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    sweet_name: Optional[str] = Field(None, max_length=50)
    ctstage_name: Optional[str] = Field(None, max_length=50)
    role: str = Field(default="user", pattern="^(user|approver|admin)$")
    approval_group_id: Optional[UUID] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating users"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating users"""
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sweet_name: Optional[str] = Field(None, max_length=50)
    ctstage_name: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, pattern="^(user|approver|admin)$")
    approval_group_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Schema for user response (without sensitive data)"""
    pass


class UserPasswordUpdate(BaseModel):
    """Schema for updating own password (requires current password)"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class AdminPasswordUpdate(BaseModel):
    """Schema for admin password reset (does not require current password)"""
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")
    reason: str = Field(default="Admin password reset", max_length=200, description="Reason for password reset")