"""
Revision Pydantic schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class RevisionBase(BaseModel):
    """Base revision schema"""
    target_article_id: str = Field(..., min_length=1, max_length=100)
    target_article_pk: str = Field(..., min_length=1, max_length=200)
    reason: str = Field(..., min_length=1)
    
    # After fields (all optional)
    after_title: Optional[str] = None
    after_info_category: Optional[str] = Field(None, max_length=50)
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[datetime] = None
    after_publish_end: Optional[datetime] = None
    after_target: Optional[str] = Field(None, max_length=100)
    after_question: Optional[str] = None
    after_answer: Optional[str] = None
    after_additional_comment: Optional[str] = None


class RevisionCreate(RevisionBase):
    """Schema for creating revisions"""
    pass


class RevisionUpdate(BaseModel):
    """Schema for updating revisions"""
    reason: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(draft|submitted|approved|rejected|deleted)$")
    
    # After fields (all optional)
    after_title: Optional[str] = None
    after_info_category: Optional[str] = Field(None, max_length=50)
    after_keywords: Optional[str] = None
    after_importance: Optional[bool] = None
    after_publish_start: Optional[datetime] = None
    after_publish_end: Optional[datetime] = None
    after_target: Optional[str] = Field(None, max_length=100)
    after_question: Optional[str] = None
    after_answer: Optional[str] = None
    after_additional_comment: Optional[str] = None


class RevisionInDB(RevisionBase):
    """Schema for revision in database"""
    revision_id: uuid.UUID
    proposer_id: uuid.UUID
    status: str
    approver_id: Optional[uuid.UUID] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Revision(RevisionInDB):
    """Schema for revision response"""
    pass