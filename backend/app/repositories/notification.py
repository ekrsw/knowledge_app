"""
Notification repository for database operations
"""
from typing import List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import SimpleNotification
from app.schemas.notification import SimpleNotificationCreate
from .base import BaseRepository


class NotificationRepository(BaseRepository[SimpleNotification, SimpleNotificationCreate, None]):
    """Repository for notification-related database operations"""
    
    def __init__(self):
        super().__init__(SimpleNotification)
    
    async def create(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: SimpleNotificationCreate
    ) -> SimpleNotification:
        """Create a new notification with proper UUID handling"""
        # Create notification model with proper UUID conversion
        obj_data = {
            "user_id": obj_in.user_id if isinstance(obj_in.user_id, UUID) else UUID(obj_in.user_id),
            "message": obj_in.message,
            "type": obj_in.type,
            "revision_id": obj_in.revision_id if obj_in.revision_id is None or isinstance(obj_in.revision_id, UUID) else UUID(obj_in.revision_id),
            "is_read": False
        }
        
        db_obj = SimpleNotification(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SimpleNotification]:
        """Get notifications for a specific user"""
        result = await db.execute(
            select(SimpleNotification)
            .where(SimpleNotification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(SimpleNotification.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_unread_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID
    ) -> List[SimpleNotification]:
        """Get unread notifications for a specific user"""
        result = await db.execute(
            select(SimpleNotification)
            .where(
                and_(
                    SimpleNotification.user_id == user_id,
                    SimpleNotification.is_read == False
                )
            )
            .order_by(SimpleNotification.created_at.desc())
        )
        return result.scalars().all()
    
    async def mark_as_read(
        self, 
        db: AsyncSession, 
        *, 
        notification_id: UUID
    ) -> SimpleNotification:
        """Mark a notification as read"""
        result = await db.execute(
            select(SimpleNotification).where(SimpleNotification.id == notification_id)
        )
        notification = result.scalars().first()
        if notification:
            notification.is_read = True
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
        return notification
    
    async def mark_all_as_read(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID
    ) -> int:
        """Mark all notifications for a user as read"""
        result = await db.execute(
            select(SimpleNotification)
            .where(
                and_(
                    SimpleNotification.user_id == user_id,
                    SimpleNotification.is_read == False
                )
            )
        )
        notifications = result.scalars().all()
        
        for notification in notifications:
            notification.is_read = True
            db.add(notification)
        
        await db.commit()
        return len(notifications)


# Create a singleton instance
notification_repository = NotificationRepository()