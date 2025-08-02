"""
Article Pydantic schemas
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    """Base article schema"""
    article_id: str = Field(..., min_length=1, max_length=100)
    article_pk: str = Field(..., min_length=1, max_length=200)
    article_number: str = Field(..., min_length=1, max_length=100)
    article_url: Optional[str] = None
    approval_group: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = None
    info_category: Optional[str] = Field(None, max_length=50)
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    publish_start: Optional[date] = None
    publish_end: Optional[date] = None
    target: Optional[str] = Field(None, max_length=100)
    question: Optional[str] = None
    answer: Optional[str] = None
    additional_comment: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Schema for creating articles"""
    pass


class ArticleUpdate(BaseModel):
    """Schema for updating articles"""
    article_pk: Optional[str] = Field(None, min_length=1, max_length=200)
    article_number: Optional[str] = Field(None, min_length=1, max_length=100)
    article_url: Optional[str] = None
    approval_group: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = None
    info_category: Optional[str] = Field(None, max_length=50)
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    publish_start: Optional[date] = None
    publish_end: Optional[date] = None
    target: Optional[str] = Field(None, max_length=100)
    question: Optional[str] = None
    answer: Optional[str] = None
    additional_comment: Optional[str] = None


class Article(ArticleBase):
    """Schema for article response"""
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True