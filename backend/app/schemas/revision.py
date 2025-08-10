"""
Revision Pydantic schemas
"""
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field


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
    approver_id: UUID


class RevisionUpdate(BaseModel):
    """Schema for updating revisions"""
    reason: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(draft|submitted|approved|rejected|deleted)$")
    
    # After fields (all optional)
    after_title: Optional[str] = None
    after_info_category: Optional[UUID] = None  # Changed to UUID type
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[datetime] = None
    after_publish_end: Optional[datetime] = None
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
    approver_id: UUID
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Revision(RevisionInDB):
    """Schema for revision response"""
    pass