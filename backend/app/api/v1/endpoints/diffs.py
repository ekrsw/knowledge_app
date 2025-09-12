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


# Removed: Complex revision comparison feature


# Removed: Formatted diff feature


# Removed: Bulk diff summaries feature


# Removed: Change statistics feature