"""
Pydantic schemas for Knowledge Revision System
"""

from .user import User, UserCreate, UserUpdate, UserInDB
from .approval_group import ApprovalGroup, ApprovalGroupCreate, ApprovalGroupUpdate
from .info_category import InfoCategory, InfoCategoryCreate, InfoCategoryUpdate
from .article import Article, ArticleCreate, ArticleUpdate
from .revision import Revision, RevisionCreate, RevisionUpdate, RevisionInDB
from .notification import SimpleNotification, SimpleNotificationCreate

__all__ = [
    "User",
    "UserCreate", 
    "UserUpdate",
    "UserInDB",
    "ApprovalGroup",
    "ApprovalGroupCreate",
    "ApprovalGroupUpdate",
    "InfoCategory",
    "InfoCategoryCreate", 
    "InfoCategoryUpdate",
    "Article",
    "ArticleCreate",
    "ArticleUpdate",
    "Revision",
    "RevisionCreate",
    "RevisionUpdate", 
    "RevisionInDB",
    "SimpleNotification",
    "SimpleNotificationCreate",
]