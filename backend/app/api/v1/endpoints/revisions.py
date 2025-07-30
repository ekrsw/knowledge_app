"""
Revision endpoints
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.revision import revision_repository
from app.schemas.revision import Revision, RevisionCreate, RevisionUpdate

router = APIRouter()


@router.get("/", response_model=List[Revision])
async def get_revisions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all revisions"""
    revisions = await revision_repository.get_multi(db, skip=skip, limit=limit)
    return revisions


@router.get("/{revision_id}", response_model=Revision)
async def get_revision(
    revision_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get revision by ID"""
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    return revision


@router.post("/", response_model=Revision, status_code=status.HTTP_201_CREATED)
async def create_revision(
    revision_in: RevisionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new revision"""
    revision = await revision_repository.create(db, obj_in=revision_in)
    return revision


@router.put("/{revision_id}", response_model=Revision)
async def update_revision(
    revision_id: UUID,
    revision_in: RevisionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update revision"""
    revision = await revision_repository.get(db, id=revision_id)
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    revision = await revision_repository.update(db, db_obj=revision, obj_in=revision_in)
    return revision


@router.get("/by-proposer/{proposer_id}", response_model=List[Revision])
async def get_revisions_by_proposer(
    proposer_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get revisions by proposer"""
    revisions = await revision_repository.get_by_proposer(
        db, proposer_id=proposer_id, skip=skip, limit=limit
    )
    return revisions


@router.get("/by-status/{status}", response_model=List[Revision])
async def get_revisions_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get revisions by status"""
    revisions = await revision_repository.get_by_status(
        db, status=status, skip=skip, limit=limit
    )
    return revisions