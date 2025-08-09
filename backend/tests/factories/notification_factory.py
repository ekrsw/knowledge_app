"""
Notification factory for test data generation
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import SimpleNotification
from app.models.user import User
from app.models.revision import Revision


class NotificationFactory:
    """Factory for creating test notifications"""
    
    _counter = 0
    
    @classmethod
    def get_next_counter(cls) -> int:
        """Get next counter value for unique identifiers"""
        cls._counter += 1
        return cls._counter
    
    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        user: Optional[User] = None,
        message: Optional[str] = None,
        type: str = "info",
        revision: Optional[Revision] = None,
        is_read: bool = False,
    ) -> SimpleNotification:
        """
        Create a test notification
        
        Args:
            db: Database session
            user: Target user (created if None)
            message: Notification message
            type: Notification type
            revision: Related revision (optional)
            is_read: Whether notification is read
        
        Returns:
            Created SimpleNotification object
        """
        counter = cls.get_next_counter()
        
        # Create default user if not provided
        if user is None:
            from .user_factory import UserFactory
            user = await UserFactory.create_user(
                db=db,
                username=f"testnotifyuser{counter}"
            )
        
        # Set default message
        if message is None:
            message = f"Test notification message {counter}"
        
        notification = SimpleNotification(
            user_id=user.id,
            message=message,
            type=type,
            revision_id=revision.revision_id if revision else None,
            is_read=is_read,
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    @classmethod
    async def create_revision_submitted(
        cls,
        db: AsyncSession,
        approver: User,
        revision: Revision,
        **kwargs
    ) -> SimpleNotification:
        """Create a revision submitted notification for approver"""
        return await cls.create(
            db=db,
            user=approver,
            message=f"新しい修正案が提出されました: {revision.target_article_id}",
            type="revision_submitted",
            revision=revision,
            **kwargs
        )
    
    @classmethod
    async def create_revision_approved(
        cls,
        db: AsyncSession,
        proposer: User,
        revision: Revision,
        **kwargs
    ) -> SimpleNotification:
        """Create a revision approved notification for proposer"""
        return await cls.create(
            db=db,
            user=proposer,
            message=f"修正案が承認されました: {revision.target_article_id}",
            type="revision_approved",
            revision=revision,
            **kwargs
        )
    
    @classmethod
    async def create_revision_rejected(
        cls,
        db: AsyncSession,
        proposer: User,
        revision: Revision,
        **kwargs
    ) -> SimpleNotification:
        """Create a revision rejected notification for proposer"""
        return await cls.create(
            db=db,
            user=proposer,
            message=f"修正案が却下されました: {revision.target_article_id}",
            type="revision_rejected",
            revision=revision,
            **kwargs
        )
    
    @classmethod
    async def create_revision_withdrawn(
        cls,
        db: AsyncSession,
        approver: User,
        revision: Revision,
        **kwargs
    ) -> SimpleNotification:
        """Create a revision withdrawn notification for approver"""
        return await cls.create(
            db=db,
            user=approver,
            message=f"修正案が撤回されました: {revision.target_article_id}",
            type="revision_withdrawn",
            revision=revision,
            **kwargs
        )
    
    @classmethod
    async def create_info_notification(
        cls,
        db: AsyncSession,
        user: Optional[User] = None,
        **kwargs
    ) -> SimpleNotification:
        """Create an info notification"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            user=user,
            message=f"Info notification {counter}",
            type="info",
            **kwargs
        )
    
    @classmethod
    async def create_warning_notification(
        cls,
        db: AsyncSession,
        user: Optional[User] = None,
        **kwargs
    ) -> SimpleNotification:
        """Create a warning notification"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            user=user,
            message=f"Warning notification {counter}",
            type="warning",
            **kwargs
        )
    
    @classmethod
    async def create_error_notification(
        cls,
        db: AsyncSession,
        user: Optional[User] = None,
        **kwargs
    ) -> SimpleNotification:
        """Create an error notification"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            user=user,
            message=f"Error notification {counter}",
            type="error",
            **kwargs
        )
    
    @classmethod
    async def create_system_notification(
        cls,
        db: AsyncSession,
        user: Optional[User] = None,
        **kwargs
    ) -> SimpleNotification:
        """Create a system notification"""
        counter = cls.get_next_counter()
        return await cls.create(
            db=db,
            user=user,
            message=f"System notification {counter}",
            type="system",
            **kwargs
        )
    
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        count: int,
        user: Optional[User] = None,
        type: str = "info",
        **kwargs
    ) -> list[SimpleNotification]:
        """Create multiple notifications at once"""
        notifications = []
        for i in range(count):
            notification = await cls.create(
                db=db,
                user=user,
                type=type,
                **kwargs
            )
            notifications.append(notification)
        
        return notifications
    
    @classmethod
    async def create_read_and_unread_mix(
        cls,
        db: AsyncSession,
        user: User,
        read_count: int = 3,
        unread_count: int = 2,
    ) -> dict[str, list[SimpleNotification]]:
        """Create a mix of read and unread notifications for testing"""
        read_notifications = await cls.create_batch(
            db=db,
            count=read_count,
            user=user,
            is_read=True
        )
        
        unread_notifications = await cls.create_batch(
            db=db,
            count=unread_count,
            user=user,
            is_read=False
        )
        
        return {
            "read": read_notifications,
            "unread": unread_notifications
        }