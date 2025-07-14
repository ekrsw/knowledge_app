from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field

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