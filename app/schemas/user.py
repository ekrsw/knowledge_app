from typing import Optional, List
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import GroupEnum


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=16)
    full_name: Optional[str] = None
    ctstage_name: Optional[str] = None
    sweet_name: Optional[str] = None
    group: GroupEnum
    is_active: bool = True
    is_admin: bool = False
    is_sv: bool = False
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """ユーザー名の詳細バリデーション"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty or whitespace only')
        if len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v.strip()) > 50:
            raise ValueError('Username must be at most 50 characters long')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """パスワードの詳細バリデーション"""
        if not v or not v.strip():
            raise ValueError('Password cannot be empty or whitespace only')
        if len(v) < 3:
            raise ValueError('Password must be at least 3 characters long')
        if len(v) > 16:
            raise ValueError('Password must be at most 16 characters long')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    ctstage_name: Optional[str] = None
    sweet_name: Optional[str] = None
    group: Optional[GroupEnum] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_sv: Optional[bool] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """ユーザー名の詳細バリデーション（更新用）"""
        if v is not None:  # Noneの場合は更新しない
            if not v or not v.strip():
                raise ValueError('Username cannot be empty or whitespace only')
            if len(v.strip()) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if len(v.strip()) > 50:
                raise ValueError('Username must be at most 50 characters long')
            return v.strip()
        return v


class PaginationParams(BaseModel):
    """ページネーション用のパラメータ"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and limit"""
        return (self.page - 1) * self.limit


class PaginatedUsers(BaseModel):
    """ページネーション付きユーザーリスト"""
    users: List[dict]  # User model will be converted to dict
    total: int = Field(description="Total number of users")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")