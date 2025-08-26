"""
Proposal management endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_approver_user
from app.services.proposal_service import proposal_service
from app.schemas.revision import Revision, RevisionCreate, RevisionUpdate
from app.models.user import User
from app.core.exceptions import (
    ProposalError,
    ProposalNotFoundError,
    ProposalPermissionError,
    ProposalStatusError,
    ProposalValidationError,
    ArticleNotFoundError
)

router = APIRouter()


# NOTE: POST /api/v1/proposals/ endpoint has been removed.
# Proposal creation should be done through POST /api/v1/revisions/ endpoint.
# The proposals endpoints are only for business actions (submit, withdraw, etc.)

@router.put("/{proposal_id}", response_model=Revision)
async def update_proposal(
    proposal_id: UUID,
    update_data: RevisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a proposal (only draft proposals)"""
    try:
        proposal = await proposal_service.update_proposal(
            db, revision_id=proposal_id, update_data=update_data, proposer=current_user
        )
        return proposal
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ProposalPermissionError, ProposalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{proposal_id}/submit", response_model=Revision)
async def submit_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit a proposal for approval"""
    try:
        proposal = await proposal_service.submit_proposal(
            db, revision_id=proposal_id, proposer=current_user
        )
        return proposal
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ProposalPermissionError, ProposalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{proposal_id}/withdraw", response_model=Revision)
async def withdraw_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Withdraw a submitted proposal back to draft"""
    try:
        proposal = await proposal_service.withdraw_proposal(
            db, revision_id=proposal_id, proposer=current_user
        )
        return proposal
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ProposalPermissionError, ProposalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{proposal_id}/approved-update", response_model=Revision)
async def update_approved_proposal(
    proposal_id: UUID,
    update_data: RevisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an approved proposal (only approver or admin can update)"""
    try:
        proposal = await proposal_service.update_approved_proposal(
            db, revision_id=proposal_id, update_data=update_data, approver=current_user
        )
        return proposal
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ProposalPermissionError, ProposalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a proposal (only draft proposals)"""
    try:
        await proposal_service.delete_proposal(
            db, revision_id=proposal_id, proposer=current_user
        )
        return None
    except ProposalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (ProposalPermissionError, ProposalStatusError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my-proposals", response_model=List[Revision])
async def get_my_proposals(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's proposals"""
    proposals = await proposal_service.get_user_proposals(
        db, user_id=current_user.id, status=status, skip=skip, limit=limit
    )
    return proposals


@router.get("/for-approval", response_model=List[Revision])
async def get_proposals_for_approval(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get proposals that need approval from current user"""
    proposals = await proposal_service.get_proposals_for_approval(
        db, approver=current_user, skip=skip, limit=limit
    )
    return proposals


@router.get("/statistics")
async def get_proposal_statistics(
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get proposal statistics"""
    # Non-admin users can only see their own statistics
    if current_user.role != "admin" and user_id is not None and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # If no user_id specified, use current user for non-admin
    if user_id is None and current_user.role != "admin":
        user_id = current_user.id
    
    stats = await proposal_service.get_proposal_statistics(db, user_id=user_id)
    return stats


@router.get("/{proposal_id}", response_model=Revision)
async def get_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific proposal"""
    from app.repositories.revision import revision_repository
    
    proposal = await revision_repository.get(db, id=proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found"
        )
    
    # Check access permissions with new rules
    # Admin can see all proposals
    if current_user.role == "admin":
        return proposal
    
    # Submitted and approved proposals are public to all authenticated users
    if proposal.status in ["submitted", "approved"]:
        return proposal
    
    # Draft and rejected proposals are only visible to the proposer
    if proposal.status in ["draft", "rejected"]:
        if proposal.proposer_id == current_user.id:
            return proposal
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this proposal"
            )
    
    # Unknown status - deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions to view this proposal"
    )