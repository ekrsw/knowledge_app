"""
Diff analysis endpoints
"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_approver_user
from app.services.diff_service import diff_service
from app.schemas.diff import RevisionDiff, DiffSummary, ArticleSnapshot, ComparisonRequest
from app.models.user import User
from app.core.exceptions import (
    ProposalNotFoundError,
    ArticleNotFoundError,
    ProposalPermissionError
)

router = APIRouter()


@router.get("/{revision_id}", response_model=RevisionDiff)
async def get_revision_diff(
    revision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed diff for a revision proposal"""
    try:
        diff = await diff_service.generate_revision_diff(db, revision_id=str(revision_id))
        
        # Check permissions
        # Users can see diffs for their own proposals
        # Approvers can see diffs for submitted proposals in their group
        # Admins can see all diffs
        if current_user.role == "admin":
            return diff
        
        # Get the revision to check permissions
        from app.repositories.revision import revision_repository
        revision = await revision_repository.get(db, id=revision_id)
        
        if not revision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Revision not found"
            )
        
        # Check if user is the proposer
        if revision.proposer_id == current_user.id:
            return diff
        
        # Check if user is an approver and revision is submitted
        if (current_user.role in ["approver", "admin"] and 
            revision.status == "submitted"):
            # Additional approval group check could be added here
            return diff
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this diff"
        )
        
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ArticleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{revision_id}/summary", response_model=DiffSummary)
async def get_diff_summary(
    revision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get summary of changes for a revision"""
    try:
        summary = await diff_service.generate_diff_summary(db, revision_id=str(revision_id))
        
        # Same permission check as full diff
        from app.repositories.revision import revision_repository
        revision = await revision_repository.get(db, id=revision_id)
        
        if not revision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Revision not found"
            )
        
        # Permission check
        if (current_user.role == "admin" or
            revision.proposer_id == current_user.id or
            (current_user.role in ["approver", "admin"] and revision.status == "submitted")):
            return summary
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this diff summary"
        )
        
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/article/{article_id}/snapshot", response_model=ArticleSnapshot)
async def get_article_snapshot(
    article_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current snapshot of an article"""
    try:
        snapshot = await diff_service.create_article_snapshot(db, article_id=article_id)
        return snapshot
        
    except ArticleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/article/{article_id}/history", response_model=List[RevisionDiff])
async def get_article_diff_history(
    article_id: str,
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get diff history for an article"""
    try:
        history = await diff_service.get_revision_history_diff(
            db, article_id=article_id, limit=limit
        )
        
        # Filter based on permissions
        if current_user.role == "admin":
            return history
        
        # For non-admin users, filter to show only:
        # - Their own proposals
        # - Submitted/approved/rejected proposals if they're an approver
        filtered_history = []
        for diff in history:
            from app.repositories.revision import revision_repository
            revision = await revision_repository.get(db, id=diff.revision_id)
            
            if revision:
                if (revision.proposer_id == current_user.id or
                    (current_user.role in ["approver", "admin"] and 
                     revision.status in ["submitted", "approved", "rejected"])):
                    filtered_history.append(diff)
        
        return filtered_history
        
    except ArticleNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/compare", response_model=Dict[str, Any])
async def compare_revisions(
    revision_id_1: UUID,
    revision_id_2: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Compare two revisions (approver/admin only)"""
    try:
        comparison = await diff_service.compare_revisions(
            db, 
            revision_id_1=str(revision_id_1),
            revision_id_2=str(revision_id_2)
        )
        return comparison
        
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{revision_id}/formatted", response_model=Dict[str, Any])
async def get_formatted_diff(
    revision_id: UUID,
    include_formatting: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get formatted diff with display-ready information"""
    try:
        # Permission check (same as regular diff)
        from app.repositories.revision import revision_repository
        revision = await revision_repository.get(db, id=revision_id)
        
        if not revision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Revision not found"
            )
        
        # Check permissions
        if (current_user.role == "admin" or
            revision.proposer_id == current_user.id or
            (current_user.role in ["approver", "admin"] and revision.status == "submitted")):
            
            formatted_diff = await diff_service.generate_formatted_diff(
                db, revision_id=str(revision_id), include_formatting=include_formatting
            )
            return formatted_diff
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this diff"
        )
        
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/bulk-summaries", response_model=List[Dict[str, Any]])
async def get_bulk_diff_summaries(
    revision_ids: List[UUID],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get summary information for multiple revisions"""
    if len(revision_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 revisions allowed per request"
        )
    
    # Convert UUIDs to strings
    revision_id_strings = [str(rid) for rid in revision_ids]
    
    # For non-admin users, filter to only their accessible revisions
    if current_user.role != "admin":
        from app.repositories.revision import revision_repository
        accessible_ids = []
        
        for revision_id in revision_id_strings:
            try:
                revision = await revision_repository.get(db, id=revision_id)
                if revision and (
                    revision.proposer_id == current_user.id or
                    (current_user.role in ["approver", "admin"] and revision.status == "submitted")
                ):
                    accessible_ids.append(revision_id)
            except Exception:
                continue
        
        revision_id_strings = accessible_ids
    
    summaries = await diff_service.get_bulk_diff_summaries(
        db, revision_ids=revision_id_strings
    )
    
    return summaries


@router.get("/statistics/changes")
async def get_change_statistics(
    days: int = Query(default=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get statistics about changes over time"""
    from datetime import datetime, timedelta
    from app.repositories.revision import revision_repository
    
    # Get revisions from the last N days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all revisions (filter by user if not admin)
    if current_user.role == "admin":
        revisions = await revision_repository.get_multi(db, limit=1000)
    else:
        revisions = await revision_repository.get_by_proposer(
            db, proposer_id=current_user.id, limit=1000
        )
    
    # Filter by date and generate statistics
    recent_revisions = [
        r for r in revisions 
        if r.created_at >= cutoff_date
    ]
    
    # Analyze changes
    stats = {
        "total_revisions": len(recent_revisions),
        "by_status": {},
        "by_impact_level": {"low": 0, "medium": 0, "high": 0, "critical": 0},
        "average_review_time": 0,
        "most_changed_fields": {}
    }
    
    total_review_time = 0
    field_changes = {}
    
    for revision in recent_revisions:
        # Count by status
        status = revision.status
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        try:
            # Generate diff to analyze impact
            diff = await diff_service.generate_revision_diff(db, revision_id=str(revision.revision_id))
            
            # Count impact levels
            stats["by_impact_level"][diff.impact_level] += 1
            
            # Add review time estimation
            summary = await diff_service.generate_diff_summary(db, revision_id=str(revision.revision_id))
            total_review_time += summary.estimated_review_time
            
            # Count field changes
            for field_diff in diff.field_diffs:
                if field_diff.change_type.value != "unchanged":
                    field_name = field_diff.field_name
                    field_changes[field_name] = field_changes.get(field_name, 0) + 1
            
        except Exception:
            # Skip revisions that can't be analyzed
            continue
    
    # Calculate averages
    if recent_revisions:
        stats["average_review_time"] = total_review_time // len(recent_revisions)
    
    # Get top 5 most changed fields
    sorted_fields = sorted(field_changes.items(), key=lambda x: x[1], reverse=True)
    stats["most_changed_fields"] = dict(sorted_fields[:5])
    
    return stats