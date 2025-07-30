"""
Article endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.article import article_repository
from app.schemas.article import Article, ArticleCreate, ArticleUpdate

router = APIRouter()


@router.get("/", response_model=List[Article])
async def get_articles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all articles"""
    articles = await article_repository.get_multi(db, skip=skip, limit=limit)
    return articles


@router.get("/{article_id}", response_model=Article)
async def get_article(
    article_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get article by ID"""
    article = await article_repository.get_by_id(db, article_id=article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    return article


@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_in: ArticleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new article"""
    # Check if article_id already exists
    existing_article = await article_repository.get_by_id(db, article_id=article_in.article_id)
    if existing_article:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article ID already exists"
        )
    
    article = await article_repository.create(db, obj_in=article_in)
    return article


@router.get("/by-category/{info_category}", response_model=List[Article])
async def get_articles_by_category(
    info_category: str,
    db: AsyncSession = Depends(get_db)
):
    """Get articles by information category"""
    articles = await article_repository.get_by_category(db, info_category=info_category)
    return articles


@router.get("/by-group/{approval_group}", response_model=List[Article])
async def get_articles_by_group(
    approval_group: str,
    db: AsyncSession = Depends(get_db)
):
    """Get articles by approval group"""
    articles = await article_repository.get_by_approval_group(db, approval_group=approval_group)
    return articles