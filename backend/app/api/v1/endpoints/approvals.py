"""
Approval management endpoints
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_approver_user, get_current_admin_user
from app.services.approval_service import approval_service
from app.schemas.approval import (
    ApprovalAction,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalHistory,
    ApprovalSummary,
    ApprovalQueue,
    ApprovalWorkload,
    ApprovalMetrics,
    BulkApprovalRequest
)
from app.schemas.revision import Revision
from app.models.user import User
from app.core.exceptions import (
    ApprovalError,
    ApprovalPermissionError,
    ApprovalStatusError,
    ProposalNotFoundError
)

router = APIRouter()


@router.post("/{revision_id}/decide", response_model=Revision)
async def process_approval_decision(
    revision_id: UUID,
    decision: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Process an approval decision for a revision"""
    try:
        revision = await approval_service.process_approval_decision(
            db, revision_id=revision_id, approver=current_user, decision=decision
        )
        return revision
        
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ApprovalPermissionError, ApprovalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/queue", response_model=List[ApprovalQueue])
async def get_approval_queue(
    priority: Optional[str] = Query(None, pattern="^(low|medium|high|urgent)$"),
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get approval queue for current approver"""
    queue = await approval_service.get_approval_queue(
        db, approver=current_user, priority_filter=priority, limit=limit
    )
    return queue


@router.get("/workload", response_model=ApprovalWorkload)
async def get_approver_workload(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get workload information for current approver"""
    workload = await approval_service.get_approver_workload(
        db, approver=current_user
    )
    return workload


# Removed: Specific approver workload feature


@router.get("/metrics", response_model=ApprovalMetrics)
async def get_approval_metrics(
    days_back: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get approval process metrics"""
    metrics = await approval_service.get_approval_metrics(
        db, days_back=days_back
    )
    return metrics


# Removed: Bulk approval feature


@router.get("/{revision_id}/can-approve")
async def can_approve_revision(
    revision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if current user can approve a specific revision"""
    can_approve = await approval_service.can_approve_revision(
        db, revision_id=revision_id, approver=current_user
    )
    
    return {"can_approve": can_approve}


@router.get("/history", response_model=List[ApprovalHistory])
async def get_approval_history(
    revision_id: Optional[UUID] = Query(None),
    approver_id: Optional[UUID] = Query(None),
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get approval history"""
    # Non-admin users can only see their own approval history
    if current_user.role != "admin":
        if approver_id is not None and approver_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        approver_id = current_user.id
    
    history = await approval_service.get_approval_history(
        db, revision_id=revision_id, approver_id=approver_id, limit=limit
    )
    
    return history


@router.get("/statistics/dashboard")
async def get_approval_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get comprehensive approval dashboard data"""
    # Get workload
    workload = await approval_service.get_approver_workload(
        db, approver=current_user
    )
    
    # Get queue
    queue = await approval_service.get_approval_queue(
        db, approver=current_user, limit=10
    )
    
    # Get metrics (if admin or approver)
    metrics = None
    if current_user.role in ["admin", "approver"]:
        metrics = await approval_service.get_approval_metrics(db, days_back=7)
    
    # Get urgent items
    urgent_queue = await approval_service.get_approval_queue(
        db, approver=current_user, priority_filter="urgent", limit=5
    )
    
    dashboard = {
        "workload": workload,
        "recent_queue": queue,
        "urgent_items": urgent_queue,
        "metrics": metrics,
        "summary": {
            "pending_count": workload.pending_count,
            "overdue_count": workload.overdue_count,
            "urgent_count": len(urgent_queue),
            "capacity_status": workload.current_capacity
        }
    }
    
    return dashboard


# Removed: Team overview feature


@router.post("/{revision_id}/quick-actions/{action}")
async def quick_approval_action(
    revision_id: UUID,
    action: ApprovalAction,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Quick approval actions with predefined settings"""
    # Create decision based on action
    decision = ApprovalDecision(
        action=action,
        comment=comment,
        priority="medium" if action == ApprovalAction.APPROVE else None
    )
    
    try:
        revision = await approval_service.process_approval_decision(
            db, revision_id=revision_id, approver=current_user, decision=decision
        )
        
        return {
            "revision_id": str(revision_id),
            "action": action.value,
            "new_status": revision.status,
            "message": f"Revision {action.value}d successfully"
        }
        
    except (ProposalNotFoundError, ApprovalPermissionError, ApprovalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Removed: Workflow recommendations feature


# Removed: Dynamic approval checklist feature