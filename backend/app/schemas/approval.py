"""
Approval-related Pydantic schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ApprovalAction(str, Enum):
    """Types of approval actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    DEFER = "defer"


class ApprovalDecision(BaseModel):
    """Schema for approval decision"""
    action: ApprovalAction
    comment: Optional[str] = Field(None, max_length=1000)
    conditions: Optional[List[str]] = Field(None, description="Conditions for approval")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    estimated_implementation_time: Optional[int] = Field(None, ge=0, description="Minutes")


class ApprovalRequest(BaseModel):
    """Schema for approval request"""
    revision_id: str
    decision: ApprovalDecision
    notify_proposer: bool = True
    escalate_if_rejected: bool = False


class ApprovalHistory(BaseModel):
    """Schema for approval history entry"""
    approval_id: str
    revision_id: str
    approver_id: str
    approver_name: str
    action: ApprovalAction
    comment: Optional[str] = None
    conditions: Optional[List[str]] = None
    priority: Optional[str] = None
    estimated_implementation_time: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalSummary(BaseModel):
    """Summary of approval process"""
    revision_id: str
    current_status: str
    approver_count: int
    pending_approvals: int
    completed_approvals: int
    rejected_count: int
    last_action: Optional[ApprovalAction] = None
    last_action_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class ApprovalQueue(BaseModel):
    """Item in approval queue"""
    revision_id: str
    target_article_id: str
    target_article_pk: str
    proposer_name: str
    reason: str
    priority: str
    impact_level: str
    total_changes: int
    critical_changes: int
    estimated_review_time: int
    submitted_at: datetime
    days_pending: int
    is_overdue: bool


class ApprovalWorkload(BaseModel):
    """Approver workload information"""
    approver_id: str
    approver_name: str
    pending_count: int
    overdue_count: int
    completed_today: int
    completed_this_week: int
    average_review_time: int
    current_capacity: str  # low, medium, high, overloaded


class ApprovalMetrics(BaseModel):
    """Approval process metrics"""
    total_pending: int
    total_overdue: int
    average_approval_time: float  # in hours
    approval_rate: float  # percentage
    rejection_rate: float  # percentage
    by_priority: Dict[str, int]
    by_impact_level: Dict[str, int]
    bottlenecks: List[str]
    performance_trends: Dict[str, Any]


class BulkApprovalRequest(BaseModel):
    """Schema for bulk approval operations"""
    revision_ids: List[str] = Field(..., max_items=20)
    decision: ApprovalDecision
    apply_same_comment: bool = True
    notify_proposers: bool = True


class ApprovalEscalation(BaseModel):
    """Schema for approval escalation"""
    revision_id: str
    original_approver_id: str
    escalated_to_id: str
    reason: str
    escalated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ApprovalDelegation(BaseModel):
    """Schema for approval delegation"""
    from_approver_id: str
    to_approver_id: str
    approval_group_id: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    reason: str
    is_active: bool
    
    class Config:
        from_attributes = True