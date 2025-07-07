from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=3, max_length=16)