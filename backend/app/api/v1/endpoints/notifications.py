"""
Enhanced notification endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_admin_user
from app.services.notification_service import notification_service
from app.repositories.notification import notification_repository
from app.schemas.notification import (
    SimpleNotification,
    SimpleNotificationCreate,
    NotificationBatch,
    NotificationStats,
    NotificationDigest,
    BulkNotificationResult
)
from app.models.user import User

router = APIRouter()


@router.get("/my-notifications", response_model=List[SimpleNotification])
async def get_my_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's notifications"""
    if unread_only:
        notifications = await notification_repository.get_unread_by_user(
            db, user_id=current_user.id
        )
        # Apply pagination manually for unread
        notifications = notifications[skip:skip+limit]
    else:
        notifications = await notification_repository.get_by_user(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    return notifications


# Removed: Notification statistics and digest features


@router.put("/{notification_id}/read", response_model=SimpleNotification)
async def mark_notification_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark notification as read"""
    # Verify ownership
    notification = await notification_repository.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if notification.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    notification = await notification_repository.mark_as_read(db, notification_id=notification_id)
    return notification


@router.put("/read-all")
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications for current user as read"""
    count = await notification_repository.mark_all_as_read(db, user_id=current_user.id)
    return {"message": f"{count}件の通知を既読にしました"}


# Removed: Batch notification creation feature


# Legacy endpoints for backward compatibility
@router.get("/{user_id}", response_model=List[SimpleNotification])
async def get_user_notifications_legacy(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get notifications for a user (legacy endpoint, admin only)"""
    notifications = await notification_repository.get_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return notifications


@router.post("/", response_model=SimpleNotification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_in: SimpleNotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new notification (legacy endpoint, admin only)"""
    notification = await notification_repository.create(db, obj_in=notification_in)
    return notification