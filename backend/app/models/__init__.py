"""
SQLAlchemy models for Knowledge Revision System
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all models with common timestamp fields"""
    
    # Common timestamp fields for all models
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo(settings.TZ)),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo(settings.TZ)),
        onupdate=lambda: datetime.now(ZoneInfo(settings.TZ)),
        nullable=False
    )


# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .approval_group import ApprovalGroup
from .info_category import InfoCategory
from .article import Article
from .revision import Revision
from .notification import SimpleNotification

__all__ = [
    "Base",
    "User",
    "ApprovalGroup", 
    "InfoCategory",
    "Article",
    "Revision",
    "SimpleNotification",
]