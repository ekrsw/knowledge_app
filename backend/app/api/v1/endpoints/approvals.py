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


@router.get("/workload/{approver_id}", response_model=ApprovalWorkload)
async def get_specific_approver_workload(
    approver_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get workload information for a specific approver (admin only)"""
    from app.repositories.user import user_repository
    
    approver = await user_repository.get(db, id=approver_id)
    if not approver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approver not found"
        )
    
    if approver.role not in ["approver", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an approver"
        )
    
    workload = await approval_service.get_approver_workload(
        db, approver=approver
    )
    return workload


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


@router.post("/bulk", response_model=Dict[str, Any])
async def process_bulk_approvals(
    bulk_request: BulkApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Process multiple approvals at once"""
    if len(bulk_request.revision_ids) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 revisions allowed per bulk operation"
        )
    
    results = await approval_service.process_bulk_approval(
        db, approver=current_user, bulk_request=bulk_request
    )
    
    return results


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


@router.get("/team-overview")
async def get_team_approval_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get team-wide approval overview (admin only)"""
    from app.repositories.user import user_repository
    
    # Get all approvers
    approvers = await user_repository.get_by_role(db, role="approver")
    admin_users = await user_repository.get_by_role(db, role="admin")
    all_approvers = approvers + admin_users
    
    team_data = []
    
    for approver in all_approvers:
        try:
            workload = await approval_service.get_approver_workload(
                db, approver=approver
            )
            team_data.append(workload)
        except Exception:
            # Skip approvers that can't be processed
            continue
    
    # Calculate team metrics
    total_pending = sum(w.pending_count for w in team_data)
    total_overdue = sum(w.overdue_count for w in team_data)
    
    # Identify bottlenecks
    overloaded_approvers = [w for w in team_data if w.current_capacity == "overloaded"]
    high_workload_approvers = [w for w in team_data if w.current_capacity == "high"]
    
    return {
        "team_workloads": team_data,
        "team_summary": {
            "total_approvers": len(team_data),
            "total_pending": total_pending,
            "total_overdue": total_overdue,
            "overloaded_count": len(overloaded_approvers),
            "high_workload_count": len(high_workload_approvers),
            "average_pending": total_pending / len(team_data) if team_data else 0
        },
        "recommendations": {
            "redistribute_workload": len(overloaded_approvers) > 0,
            "urgent_attention_needed": total_overdue > 10,
            "team_capacity_status": "overloaded" if len(overloaded_approvers) > len(team_data) // 2 else "normal"
        }
    }


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


@router.get("/workflow/recommendations")
async def get_workflow_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get workflow recommendations for improving approval efficiency"""
    from app.utils.approval_workflow import approval_workflow_utils
    
    # Get approver's queue and workload
    queue = await approval_service.get_approval_queue(
        db, approver=current_user, limit=100
    )
    workload = await approval_service.get_approver_workload(
        db, approver=current_user
    )
    
    # Generate recommendations
    recommendations = approval_workflow_utils.generate_approval_recommendations(
        queue, workload.current_capacity
    )
    
    # Calculate workflow metrics
    metrics = approval_workflow_utils.calculate_workflow_metrics(queue)
    
    return {
        "recommendations": recommendations,
        "workflow_metrics": metrics,
        "queue_summary": {
            "total_items": len(queue),
            "urgent_items": len([q for q in queue if q.priority == "urgent"]),
            "overdue_items": len([q for q in queue if q.is_overdue]),
            "capacity_status": workload.current_capacity
        }
    }


@router.get("/workflow/checklist/{revision_id}")
async def get_approval_checklist(
    revision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get dynamic approval checklist for a revision"""
    from app.utils.approval_workflow import approval_workflow_utils
    from app.services.diff_service import diff_service
    
    # Check permissions
    can_approve = await approval_service.can_approve_revision(
        db, revision_id=revision_id, approver=current_user
    )
    
    if not can_approve:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to approve this revision"
        )
    
    try:
        # Get diff information
        diff = await diff_service.generate_revision_diff(
            db, revision_id=str(revision_id)
        )
        
        # Generate checklist
        checklist = approval_workflow_utils.create_approval_checklist(
            diff.impact_level,
            diff.critical_changes,
            diff.change_categories
        )
        
        return {
            "revision_id": str(revision_id),
            "checklist": checklist,
            "summary": {
                "total_items": len(checklist),
                "required_items": len([item for item in checklist if item["required"]]),
                "estimated_time": sum(5 if item["required"] else 2 for item in checklist)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not generate checklist: {str(e)}"
        )