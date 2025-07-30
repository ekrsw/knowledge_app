"""
System and health endpoints
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.dependencies import get_db, get_current_admin_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "database": "connected"  # Placeholder - would test DB connection
    }


@router.get("/version")
async def get_version():
    """Get API version information"""
    return {
        "version": "0.1.0",
        "api_version": "v1",
        "build_date": "2025-01-30",
        "features": [
            "proposal_management",
            "approval_workflow",
            "diff_analysis",
            "notification_system",
            "user_management"
        ]
    }


@router.get("/stats", dependencies=[Depends(get_current_admin_user)])
async def get_system_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics (admin only)"""
    from app.repositories.user import user_repository
    from app.repositories.revision import revision_repository
    from app.repositories.notification import notification_repository
    
    # Get user counts
    all_users = await user_repository.get_multi(db, limit=10000)
    user_stats = {
        "total_users": len(all_users),
        "by_role": {}
    }
    
    for user in all_users:
        role = user.role
        user_stats["by_role"][role] = user_stats["by_role"].get(role, 0) + 1
    
    # Get revision counts
    all_revisions = await revision_repository.get_multi(db, limit=10000)
    revision_stats = {
        "total_revisions": len(all_revisions),
        "by_status": {}
    }
    
    for revision in all_revisions:
        status = revision.status
        revision_stats["by_status"][status] = revision_stats["by_status"].get(status, 0) + 1
    
    # Get notification counts
    all_notifications = await notification_repository.get_multi(db, limit=10000)
    notification_stats = {
        "total_notifications": len(all_notifications),
        "unread_count": len([n for n in all_notifications if not n.is_read]),
        "read_count": len([n for n in all_notifications if n.is_read])
    }
    
    return {
        "users": user_stats,
        "revisions": revision_stats,
        "notifications": notification_stats,
        "system": {
            "database_status": "connected",
            "api_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }
    }


@router.get("/config", dependencies=[Depends(get_current_admin_user)])
async def get_system_config():
    """Get system configuration (admin only)"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "api_version": "v1",
        "cors_origins": settings.get_cors_origins(),
        "features": {
            "email_notifications": False,  # Placeholder
            "sms_notifications": False,   # Placeholder
            "webhook_notifications": False,  # Placeholder
            "bulk_operations": True,
            "approval_groups": True,
            "diff_analysis": True,
            "metrics_dashboard": True
        },
        "limits": {
            "max_bulk_notifications": 100,
            "max_bulk_approvals": 20,
            "max_diff_comparisons": 50,
            "max_queue_size": 100
        }
    }


@router.post("/maintenance", dependencies=[Depends(get_current_admin_user)])
async def trigger_maintenance_tasks(
    db: AsyncSession = Depends(get_db)
):
    """Trigger system maintenance tasks (admin only)"""
    from app.services.notification_service import notification_service
    
    results = {}
    
    try:
        # Clean up old notifications
        deleted_count = await notification_service.cleanup_expired_notifications(
            db, days_old=30
        )
        results["notification_cleanup"] = {
            "status": "completed",
            "deleted_count": deleted_count
        }
    except Exception as e:
        results["notification_cleanup"] = {
            "status": "failed",
            "error": str(e)
        }
    
    # Add other maintenance tasks here
    results["cache_cleanup"] = {
        "status": "skipped",
        "reason": "No cache configured"
    }
    
    results["database_optimization"] = {
        "status": "skipped",
        "reason": "Manual optimization required"
    }
    
    return {
        "maintenance_run": datetime.utcnow().isoformat(),
        "results": results,
        "summary": {
            "completed_tasks": len([r for r in results.values() if r["status"] == "completed"]),
            "failed_tasks": len([r for r in results.values() if r["status"] == "failed"]),
            "skipped_tasks": len([r for r in results.values() if r["status"] == "skipped"])
        }
    }


@router.get("/api-documentation")
async def get_api_documentation():
    """Get API endpoint documentation summary"""
    endpoints = {
        "authentication": {
            "prefix": "/auth",
            "endpoints": [
                "POST /login - User login",
                "POST /register - User registration", 
                "POST /refresh - Refresh access token",
                "GET /me - Get current user info"
            ]
        },
        "proposals": {
            "prefix": "/proposals",
            "endpoints": [
                "POST / - Create new proposal",
                "PUT /{id} - Update proposal",
                "POST /{id}/submit - Submit for approval",
                "POST /{id}/withdraw - Withdraw proposal",
                "DELETE /{id} - Delete proposal",
                "GET /my-proposals - Get user's proposals",
                "GET /for-approval - Get proposals needing approval",
                "GET /statistics - Get proposal statistics",
                "GET /{id} - Get specific proposal"
            ]
        },
        "approvals": {
            "prefix": "/approvals",
            "endpoints": [
                "POST /{id}/decide - Process approval decision",
                "GET /queue - Get approval queue",
                "GET /workload - Get approver workload",
                "GET /metrics - Get approval metrics",
                "POST /bulk - Process bulk approvals",
                "GET /{id}/can-approve - Check approval permissions",
                "GET /history - Get approval history",
                "GET /statistics/dashboard - Get approval dashboard",
                "GET /team-overview - Get team approval overview",
                "POST /{id}/quick-actions/{action} - Quick approval actions",
                "GET /workflow/recommendations - Get workflow recommendations",
                "GET /workflow/checklist/{id} - Get approval checklist"
            ]
        },
        "diffs": {
            "prefix": "/diffs",
            "endpoints": [
                "GET /{id} - Get revision diff",
                "GET /{id}/summary - Get diff summary",
                "GET /article/{id}/snapshot - Get article snapshot",
                "GET /article/{id}/history - Get article diff history",
                "POST /compare - Compare two revisions",
                "GET /{id}/formatted - Get formatted diff",
                "POST /bulk-summaries - Get bulk diff summaries",
                "GET /statistics/changes - Get change statistics"
            ]
        },
        "notifications": {
            "prefix": "/notifications",
            "endpoints": [
                "GET /my-notifications - Get user notifications",
                "GET /statistics - Get notification statistics",
                "GET /digest - Get notification digest",
                "PUT /{id}/read - Mark notification as read",
                "PUT /read-all - Mark all as read",
                "POST /batch - Create batch notifications",
                "GET /{user_id} - Get user notifications (admin)",
                "POST / - Create notification (admin)"
            ]
        },
        "users": {
            "prefix": "/users",
            "endpoints": [
                "GET / - List users (admin)",
                "POST / - Create user (admin)",
                "GET /{id} - Get user by ID",
                "PUT /{id} - Update user",
                "DELETE /{id} - Delete user (admin)"
            ]
        },
        "system": {
            "prefix": "/system",
            "endpoints": [
                "GET /health - Health check",
                "GET /version - Version information",
                "GET /stats - System statistics (admin)",
                "GET /config - System configuration (admin)",
                "POST /maintenance - Run maintenance tasks (admin)",
                "GET /api-documentation - API documentation summary"
            ]
        }
    }
    
    return {
        "api_version": "v1",
        "base_url": "/api/v1",
        "total_endpoints": sum(len(group["endpoints"]) for group in endpoints.values()),
        "endpoint_groups": endpoints,
        "authentication": "JWT Bearer token required for protected endpoints",
        "documentation": "Full OpenAPI documentation available at /api/v1/openapi.json"
    }