"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, revisions, articles, info_categories, approval_groups, notifications, proposals, diffs, approvals, system, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(diffs.router, prefix="/diffs", tags=["diffs"])
api_router.include_router(revisions.router, prefix="/revisions", tags=["revisions"])
api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(info_categories.router, prefix="/info-categories", tags=["info-categories"])
api_router.include_router(approval_groups.router, prefix="/approval-groups", tags=["approval-groups"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])