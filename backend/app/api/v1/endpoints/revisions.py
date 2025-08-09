"""
Revision endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_approver_user
from app.repositories.revision import revision_repository
from app.repositories.user import user_repository
from app.schemas.revision import Revision, RevisionCreate, RevisionUpdate
from app.models.user import User
from app.models.revision import Revision as RevisionModel

router = APIRouter()


@router.get("/", response_model=List[Revision])
async def get_revisions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revisions based on user permissions
    - Admin: can see all revisions
    - Approver: can see revisions for their approval groups
    - Regular user: can only see their own revisions
    """
    if current_user.role == "admin":
        revisions = await revision_repository.get_multi(db, skip=skip, limit=limit)
    elif current_user.role == "approver":
        # Get revisions for articles that belong to user's approval group
        if current_user.approval_group_id:
            revisions = await revision_repository.get_by_approver_groups(
                db, approval_group_ids=[current_user.approval_group_id], skip=skip, limit=limit
            )
        else:
            revisions = []
    else:
        # Regular users only see their own revisions
        revisions = await revision_repository.get_by_proposer(
            db, proposer_id=current_user.id, skip=skip, limit=limit
        )
    return revisions


@router.get("/{revision_id}", response_model=Revision)
async def get_revision(
    revision_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revision by ID with permission check"""
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    # Permission check
    if current_user.role == "admin":
        # Admin can see all revisions
        pass
    elif current_user.role == "approver" and revision.after_info_category_obj:
        # Approver can see revisions for their approval groups
        article = await revision_repository.get_target_article(db, revision_id=revision_id)
        if article and article.approval_group != current_user.approval_group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to view this revision"
            )
    else:
        # Regular users can only see their own revisions
        if revision.proposer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to view this revision"
            )
    
    return revision


@router.post("/", response_model=Revision, status_code=status.HTTP_201_CREATED)
async def create_revision(
    revision_in: RevisionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new revision with proposer_id automatically set from current user"""
    # Create revision with proposer_id from current user
    revision_data = revision_in.model_dump()
    revision_data["proposer_id"] = current_user.id
    revision = await revision_repository.create_with_proposer(db, obj_in=revision_data)
    return revision


@router.put("/{revision_id}", response_model=Revision)
async def update_revision(
    revision_id: UUID,
    revision_in: RevisionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update revision - only proposer can update their draft revisions"""
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    # Only the proposer can update their revision
    if revision.proposer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own revisions"
        )
    
    # Only draft revisions can be updated
    if revision.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update revision with status '{revision.status}'. Only draft revisions can be updated."
        )
    
    revision = await revision_repository.update(db, db_obj=revision, obj_in=revision_in)
    return revision


@router.get("/by-proposer/{proposer_id}", response_model=List[Revision])
async def get_revisions_by_proposer(
    proposer_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revisions by proposer with permission check"""
    # Only admin or the proposer themselves can access this endpoint
    if current_user.role != "admin" and current_user.id != proposer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own revisions"
        )
    
    revisions = await revision_repository.get_by_proposer(
        db, proposer_id=proposer_id, skip=skip, limit=limit
    )
    return revisions


@router.get("/by-status/{status}", response_model=List[Revision])
async def get_revisions_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revisions by status with permission filtering"""
    if current_user.role == "admin":
        revisions = await revision_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )
    elif current_user.role == "approver":
        # Approvers see revisions for their approval groups
        if current_user.approval_group_id:
            revisions = await revision_repository.get_by_status_and_approver_groups(
                db, status=status, approval_group_ids=[current_user.approval_group_id], 
                skip=skip, limit=limit
            )
        else:
            revisions = []
    else:
        # Regular users only see their own revisions
        revisions = await revision_repository.get_by_status_and_proposer(
            db, status=status, proposer_id=current_user.id, 
            skip=skip, limit=limit
        )
    return revisions


@router.patch("/{revision_id}/status", response_model=Revision)
async def update_revision_status(
    revision_id: UUID,
    status: str,
    current_user: User = Depends(get_current_approver_user),
    db: AsyncSession = Depends(get_db)
):
    """Update revision status - requires approver or admin role"""
    from datetime import datetime
    
    # Validate status
    valid_statuses = ["submitted", "approved", "rejected", "deleted"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    # Check if approver has permission for this revision's article
    if current_user.role == "approver":
        article = await revision_repository.get_target_article(db, revision_id=revision_id)
        if article and article.approval_group != current_user.approval_group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to approve revisions for this article's approval group"
            )
    
    # Update status and set approver/processed time for approval/rejection
    update_data = {"status": status}
    if status in ["approved", "rejected"]:
        update_data["approver_id"] = current_user.id
        update_data["processed_at"] = datetime.utcnow()
    
    revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
    return revision