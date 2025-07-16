from typing import Optional
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