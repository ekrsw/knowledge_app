"""
Diff-related Pydantic schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ChangeType(str, Enum):
    """Types of changes in a diff"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


class FieldDiff(BaseModel):
    """Difference information for a single field"""
    field_name: str
    field_label: str
    change_type: ChangeType
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    formatted_old_value: Optional[str] = None
    formatted_new_value: Optional[str] = None
    is_critical: bool = False
    description: Optional[str] = None


class RevisionDiff(BaseModel):
    """Complete diff information for a revision"""
    revision_id: str
    target_article_id: str
    target_article_pk: str
    proposer_name: str
    reason: str
    status: str
    created_at: datetime
    
    # Field differences
    field_diffs: List[FieldDiff]
    
    # Summary information
    total_changes: int
    critical_changes: int
    change_categories: List[str]
    impact_level: str  # low, medium, high, critical


class DiffSummary(BaseModel):
    """Summary of differences"""
    total_changes: int
    changes_by_type: Dict[str, int]
    changes_by_category: Dict[str, int]
    critical_changes: int
    impact_level: str
    estimated_review_time: int  # in minutes


class ArticleSnapshot(BaseModel):
    """Snapshot of article data at a point in time"""
    article_id: str
    article_pk: str
    title: Optional[str] = None
    info_category: Optional[str] = None
    keywords: Optional[str] = None
    importance: Optional[bool] = None
    publish_start: Optional[datetime] = None
    publish_end: Optional[datetime] = None
    target: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    additional_comment: Optional[str] = None
    snapshot_time: datetime


class ComparisonRequest(BaseModel):
    """Request for comparing two versions"""
    article_id: str
    revision_id: Optional[str] = None
    compare_with_current: bool = True
    include_formatting: bool = True
    include_metadata: bool = True