"""
Information Category endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.info_category import info_category_repository
from app.schemas.info_category import InfoCategory, InfoCategoryCreate, InfoCategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[InfoCategory])
async def get_info_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all information categories"""
    categories = await info_category_repository.get_multi(db, skip=skip, limit=limit)
    return categories


@router.get("/active", response_model=List[InfoCategory])
async def get_active_info_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all active information categories"""
    categories = await info_category_repository.get_active_categories(db)
    return categories


@router.get("/{category_id}", response_model=InfoCategory)
async def get_info_category(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get information category by ID"""
    category = await info_category_repository.get_by_id(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Information category not found"
        )
    return category


@router.post("/", response_model=InfoCategory, status_code=status.HTTP_201_CREATED)
async def create_info_category(
    category_in: InfoCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new information category"""
    # Check if category_id already exists
    existing_category = await info_category_repository.get_by_id(db, category_id=category_in.category_id)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category ID already exists"
        )
    
    category = await info_category_repository.create(db, obj_in=category_in)
    return category


@router.put("/{category_id}", response_model=InfoCategory)
async def update_info_category(
    category_id: str,
    category_in: InfoCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update information category"""
    category = await info_category_repository.get_by_id(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Information category not found"
        )
    
    category = await info_category_repository.update(db, db_obj=category, obj_in=category_in)
    return category