"""
SQLAlchemy models for Knowledge Revision System
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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