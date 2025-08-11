"""
Approval Group endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_admin_user
from app.repositories.approval_group import approval_group_repository
from app.schemas.approval_group import ApprovalGroup, ApprovalGroupCreate, ApprovalGroupUpdate
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[ApprovalGroup])
async def get_approval_groups(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all approval groups"""
    groups = await approval_group_repository.get_multi(db, skip=skip, limit=limit)
    return groups


@router.get("/{group_id}", response_model=ApprovalGroup)
async def get_approval_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get approval group by ID"""
    group = await approval_group_repository.get_by_id(db, group_id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval group not found"
        )
    return group


@router.post("/", response_model=ApprovalGroup, status_code=status.HTTP_201_CREATED)
async def create_approval_group(
    group_in: ApprovalGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new approval group"""
    # group_id は自動生成されるため、重複チェック不要
    group = await approval_group_repository.create(db, obj_in=group_in)
    return group


@router.put("/{group_id}", response_model=ApprovalGroup)
async def update_approval_group(
    group_id: UUID,
    group_in: ApprovalGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update approval group"""
    group = await approval_group_repository.get_by_id(db, group_id=group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval group not found"
        )
    
    group = await approval_group_repository.update(db, db_obj=group, obj_in=group_in)
    return group