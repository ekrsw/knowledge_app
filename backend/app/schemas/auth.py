"""
Authentication Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration schema"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    sweet_name: Optional[str] = None
    ctstage_name: Optional[str] = None