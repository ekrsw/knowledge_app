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
from app.schemas.revision import Revision, RevisionCreate, RevisionUpdate, RevisionStatusUpdate, RevisionWithNames
from app.models.user import User
from app.models.revision import Revision as RevisionModel

router = APIRouter()


@router.get("/", response_model=List[RevisionWithNames])
async def get_revisions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revisions based on user permissions with proposer and approver names
    - Admin: can see all revisions
    - All authenticated users: can see submitted/approved revisions + their own draft/rejected
    """
    if current_user.role == "admin":
        # Admin can see all revisions with names
        revisions = await revision_repository.get_with_names(db, skip=skip, limit=limit)
    else:
        # All users can see:
        # 1. Public revisions (submitted/approved by anyone)
        # 2. Their own private revisions (draft/rejected)
        revisions = await revision_repository.get_mixed_access_with_names(
            db, user_id=current_user.id, skip=skip, limit=limit
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
    elif revision.status in ["submitted", "approved"]:
        # All authenticated users can see submitted/approved revisions
        pass
    elif revision.status == "draft":
        # Only the proposer can see draft revisions
        if revision.proposer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to view this revision"
            )
    elif revision.status == "rejected":
        # Proposer and approver can see rejected revisions
        if revision.proposer_id != current_user.id and revision.approver_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to view this revision"
            )
    else:
        # Unknown status - deny access
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
    # Validate target article exists
    from app.repositories.article import article_repository
    article = await article_repository.get_by_id(db, article_id=revision_in.target_article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target article not found"
        )
    
    # Validate approver exists (only if approver_id is provided)
    if revision_in.approver_id:
        from app.repositories.user import user_repository
        approver = await user_repository.get(db, id=revision_in.approver_id)
        if not approver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified approver not found"
            )
    
    # Validate info category if provided
    if revision_in.after_info_category:
        from app.repositories.info_category import info_category_repository
        from sqlalchemy import select
        from app.models.info_category import InfoCategory
        
        # Use direct query since InfoCategory uses category_id as primary key
        result = await db.execute(
            select(InfoCategory).where(InfoCategory.category_id == revision_in.after_info_category)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specified info category not found"
            )
    
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
    """Update revision - proposer can update draft revisions, approver can update approved revisions"""
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    # Check permissions based on status
    if revision.status == "draft":
        # Only the proposer can update draft revisions
        if revision.proposer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own draft revisions"
            )
    elif revision.status == "approved":
        # Only the approver or admin can update approved revisions
        if revision.approver_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the designated approver or admin can update approved revisions"
            )
        # Prevent modification of core metadata fields for approved revisions
        if revision_in.status is not None:
            revision_in.status = None
    else:
        # No other statuses can be updated
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update revision with status '{revision.status}'. Only draft and approved revisions can be updated."
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
        # Admin can see all revisions with any status
        revisions = await revision_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )
    elif status in ["submitted", "approved"]:
        # All users can see public status revisions
        revisions = await revision_repository.get_by_status(
            db, status=status, skip=skip, limit=limit
        )
    elif status == "draft":
        # Only user's own draft revisions
        revisions = await revision_repository.get_by_status_and_proposer(
            db, status=status, proposer_id=current_user.id, 
            skip=skip, limit=limit
        )
    elif status == "rejected":
        # For rejected: proposer and approver can see
        from sqlalchemy import select, and_, or_
        from app.models.revision import Revision
        
        result = await db.execute(
            select(Revision)
            .where(
                and_(
                    Revision.status == "rejected",
                    or_(
                        Revision.proposer_id == current_user.id,
                        Revision.approver_id == current_user.id
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(Revision.created_at.desc())
        )
        revisions = result.scalars().all()
    else:
        # Unknown status
        revisions = []
    return revisions


@router.get("/by-article/{target_article_id}", response_model=List[Revision])
async def get_revisions_by_article(
    target_article_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get public revisions (submitted/approved) for a specific article
    - All authenticated users can access this endpoint
    - Only returns submitted and approved revisions (public revisions)
    """
    revisions = await revision_repository.get_public_revisions_by_article(
        db, target_article_id=target_article_id, skip=skip, limit=limit
    )
    return revisions


@router.patch("/{revision_id}/status", response_model=Revision)
async def update_revision_status(
    revision_id: UUID,
    status_update: RevisionStatusUpdate,
    current_user: User = Depends(get_current_approver_user),
    db: AsyncSession = Depends(get_db)
):
    """Update revision status - requires approver or admin role"""
    from datetime import datetime
    
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
    update_data = {"status": status_update.status}
    if status_update.status in ["approved", "rejected"]:
        update_data["approver_id"] = current_user.id
        update_data["processed_at"] = datetime.utcnow()
    
    revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
    return revision