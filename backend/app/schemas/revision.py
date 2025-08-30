"""
Revision Pydantic schemas
"""
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class RevisionBase(BaseModel):
    """Base revision schema"""
    target_article_id: str = Field(..., min_length=1, max_length=100)
    # target_article_pk: removed field
    reason: str = Field(..., min_length=1)
    
    # After fields (all optional)
    after_title: Optional[str] = None
    after_info_category: Optional[UUID] = None  # Changed to UUID type
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[date] = None
    after_publish_end: Optional[date] = None
    after_target: Optional[str] = Field(None, max_length=100)
    after_question: Optional[str] = None
    after_answer: Optional[str] = None
    after_additional_comment: Optional[str] = None


class RevisionCreate(RevisionBase):
    """Schema for creating revisions"""
    approver_id: Optional[UUID] = None
    
    @field_validator('after_publish_start', 'after_publish_end', mode='before')
    @classmethod
    def parse_empty_date(cls, v):
        """Convert empty string to None for optional date fields"""
        if v == "":
            return None
        return v
    
    @field_validator('approver_id', mode='before')
    @classmethod
    def parse_empty_uuid(cls, v):
        """Convert empty string to None for optional UUID fields"""
        if v == "":
            return None
        return v


class RevisionUpdate(BaseModel):
    """Schema for updating revisions"""
    reason: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(draft|submitted|approved|rejected|deleted)$")
    processed_at: Optional[datetime] = None  # Add processed_at field
    approver_id: Optional[UUID] = None  # Add approver_id field
    
    # After fields (all optional)
    after_title: Optional[str] = None
    after_info_category: Optional[UUID] = None  # Changed to UUID type
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[date] = None
    after_publish_end: Optional[date] = None
    after_target: Optional[str] = Field(None, max_length=100)
    after_question: Optional[str] = None
    after_answer: Optional[str] = None
    after_additional_comment: Optional[str] = None


class RevisionStatusUpdate(BaseModel):
    """Schema for updating revision status"""
    status: str = Field(..., pattern="^(submitted|approved|rejected|deleted)$")


class RevisionInDB(RevisionBase):
    """Schema for revision in database"""
    revision_id: UUID
    proposer_id: UUID
    status: str
    approver_id: Optional[UUID] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Revision(RevisionInDB):
    """Schema for revision response"""
    pass


class RevisionWithNames(BaseModel):
    """Schema for revision response with user names instead of IDs, and article number"""
    revision_id: UUID
    article_number: Optional[str] = None  # Article number from Article table
    reason: str
    after_title: Optional[str] = None
    after_info_category: Optional[UUID] = None
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[date] = None
    after_publish_end: Optional[date] = None
    after_target: Optional[str] = Field(None, max_length=100)
    after_question: Optional[str] = None
    after_answer: Optional[str] = None
    after_additional_comment: Optional[str] = None
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # User names instead of IDs
    proposer_name: str
    approver_name: Optional[str] = None
    
    class Config:
        from_attributes = True