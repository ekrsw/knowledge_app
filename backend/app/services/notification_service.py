"""
Notification service for managing system notifications
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.revision import Revision
from app.repositories.notification import notification_repository
from app.repositories.user import user_repository
from app.repositories.revision import revision_repository
from app.schemas.notification import (
    NotificationType,
    NotificationPriority,
    NotificationChannel,
    EnhancedNotificationCreate,
    NotificationTemplate,
    NotificationBatch,
    NotificationPreferences,
    NotificationStats,
    NotificationDigest,
    BulkNotificationResult,
    SimpleNotificationCreate,
    SimpleNotification
)


class NotificationService:
    """Service for managing notifications"""
    
    # Default notification templates
    DEFAULT_TEMPLATES = {
        NotificationType.PROPOSAL_SUBMITTED: {
            "title": "新しい修正提案が提出されました",
            "message": "{proposer_name}さんが記事「{article_title}」の修正提案を提出しました。確認をお願いします。",
            "priority": NotificationPriority.MEDIUM,
            "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        },
        NotificationType.PROPOSAL_APPROVED: {
            "title": "修正提案が承認されました",
            "message": "あなたの修正提案「{article_title}」が{approver_name}さんに承認されました。",
            "priority": NotificationPriority.HIGH,
            "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        },
        NotificationType.PROPOSAL_REJECTED: {
            "title": "修正提案が却下されました",
            "message": "あなたの修正提案「{article_title}」が{approver_name}さんに却下されました。理由: {reason}",
            "priority": NotificationPriority.HIGH,
            "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        },
        NotificationType.PROPOSAL_CHANGES_REQUESTED: {
            "title": "修正提案に変更が要求されました",
            "message": "あなたの修正提案「{article_title}」について{approver_name}さんから変更要求があります。",
            "priority": NotificationPriority.MEDIUM,
            "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        },
        NotificationType.APPROVAL_OVERDUE: {
            "title": "承認期限が近づいています",
            "message": "修正提案「{article_title}」の承認期限が{days_overdue}日超過しています。",
            "priority": NotificationPriority.URGENT,
            "channels": [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        }
    }
    
    async def create_notification_from_template(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        template_variables: Dict[str, Any],
        revision_id: Optional[UUID] = None,
        channels: Optional[List[NotificationChannel]] = None
    ) -> SimpleNotification:
        """Create notification from template"""
        template = self.DEFAULT_TEMPLATES.get(notification_type)
        if not template:
            raise ValueError(f"No template found for notification type: {notification_type}")
        
        # Format message with variables
        try:
            title = template["title"].format(**template_variables)
            message = template["message"].format(**template_variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
        
        # Use template channels or provided channels
        notification_channels = channels or template["channels"]
        
        # Create simple notification (using existing repository)
        notification_data = SimpleNotificationCreate(
            user_id=user_id,
            type=notification_type.value,
            message=f"{title}: {message}",
            revision_id=revision_id
        )
        
        notification = await notification_repository.create(db, obj_in=notification_data)
        
        # Send to external channels if needed
        if NotificationChannel.EMAIL in notification_channels:
            await self._send_email_notification(user_id, title, message)
        
        return notification
    
    async def _send_email_notification(
        self,
        user_id: UUID,
        title: str,
        message: str
    ) -> bool:
        """Send email notification (placeholder implementation)"""
        # In a real implementation, this would integrate with an email service
        print(f"[EMAIL] To User {user_id}: {title} - {message}")
        return True
    
    async def notify_proposal_submitted(
        self,
        db: AsyncSession,
        *,
        revision: Revision,
        approvers: List[User]
    ) -> List[SimpleNotification]:
        """Notify approvers when a proposal is submitted"""
        # Get proposer and article information
        proposer = await user_repository.get(db, id=revision.proposer_id)
        proposer_name = proposer.full_name if proposer else "Unknown User"
        
        # Get article title (simplified - would normally fetch from article)
        article_title = f"記事 {revision.target_article_id}"
        
        notifications = []
        
        for approver in approvers:
            try:
                notification = await self.create_notification_from_template(
                    db,
                    user_id=approver.id,
                    notification_type=NotificationType.PROPOSAL_SUBMITTED,
                    template_variables={
                        "proposer_name": proposer_name,
                        "article_title": article_title
                    },
                    revision_id=revision.revision_id
                )
                notifications.append(notification)
            except Exception as e:
                print(f"Failed to notify approver {approver.id}: {e}")
                continue
        
        return notifications
    
    async def notify_proposal_decision(
        self,
        db: AsyncSession,
        *,
        revision: Revision,
        approver: User,
        decision: str,
        comment: Optional[str] = None
    ) -> Optional[SimpleNotification]:
        """Notify proposer about approval decision"""
        # Get proposer
        proposer = await user_repository.get(db, id=revision.proposer_id)
        if not proposer:
            return None
        
        # Determine notification type based on decision
        notification_type_map = {
            "approved": NotificationType.PROPOSAL_APPROVED,
            "rejected": NotificationType.PROPOSAL_REJECTED,
            "draft": NotificationType.PROPOSAL_CHANGES_REQUESTED  # Changes requested
        }
        
        notification_type = notification_type_map.get(revision.status)
        if not notification_type:
            return None
        
        # Get article title
        article_title = f"記事 {revision.target_article_id}"
        
        template_variables = {
            "approver_name": approver.full_name,
            "article_title": article_title
        }
        
        if comment:
            template_variables["reason"] = comment
        
        try:
            notification = await self.create_notification_from_template(
                db,
                user_id=proposer.id,
                notification_type=notification_type,
                template_variables=template_variables,
                revision_id=revision.revision_id
            )
            return notification
        except Exception as e:
            print(f"Failed to notify proposer {proposer.id}: {e}")
            return None
    
    async def notify_overdue_approvals(
        self,
        db: AsyncSession,
        *,
        days_threshold: int = 3
    ) -> List[SimpleNotification]:
        """Notify about overdue approvals"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        # Get overdue submitted revisions
        submitted_revisions = await revision_repository.get_by_status(
            db, status="submitted", limit=1000
        )
        
        overdue_revisions = [
            r for r in submitted_revisions 
            if r.created_at <= cutoff_date
        ]
        
        notifications = []
        
        # Group by potential approvers (simplified - would normally use approval groups)
        approvers = await user_repository.get_by_role(db, role="approver")
        admin_users = await user_repository.get_by_role(db, role="admin")
        all_approvers = approvers + admin_users
        
        for revision in overdue_revisions:
            days_overdue = (datetime.utcnow() - revision.created_at).days
            article_title = f"記事 {revision.target_article_id}"
            
            for approver in all_approvers:
                try:
                    notification = await self.create_notification_from_template(
                        db,
                        user_id=approver.id,
                        notification_type=NotificationType.APPROVAL_OVERDUE,
                        template_variables={
                            "article_title": article_title,
                            "days_overdue": days_overdue
                        },
                        revision_id=revision.revision_id
                    )
                    notifications.append(notification)
                except Exception:
                    continue
        
        return notifications
    
    async def create_batch_notification(
        self,
        db: AsyncSession,
        *,
        batch_request: NotificationBatch
    ) -> BulkNotificationResult:
        """Create notifications for multiple users"""
        start_time = datetime.utcnow()
        batch_id = str(uuid4())
        
        successful_count = 0
        failed_users = []
        errors = []
        
        for user_id in batch_request.user_ids:
            try:
                notification_data = SimpleNotificationCreate(
                    user_id=user_id,
                    type=batch_request.notification_type.value,
                    message=f"{batch_request.title}: {batch_request.message}"
                )
                
                await notification_repository.create(db, obj_in=notification_data)
                successful_count += 1
                
            except Exception as e:
                failed_users.append(str(user_id))
                errors.append(f"User {user_id}: {str(e)}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return BulkNotificationResult(
            total_requested=len(batch_request.user_ids),
            successfully_created=successful_count,
            failed_count=len(failed_users),
            failed_users=failed_users,
            errors=errors,
            batch_id=batch_id,
            processing_time_ms=int(processing_time)
        )
    
    async def get_user_notification_stats(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        days_back: int = 30
    ) -> NotificationStats:
        """Get notification statistics for a user"""
        # Get user's notifications
        notifications = await notification_repository.get_by_user(
            db, user_id=user_id, limit=1000
        )
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        recent_notifications = [
            n for n in notifications 
            if n.created_at >= cutoff_date
        ]
        
        total_count = len(recent_notifications)
        unread_count = len([n for n in recent_notifications if not n.is_read])
        read_count = total_count - unread_count
        
        # Group by type
        by_type = {}
        for notification in recent_notifications:
            notification_type = notification.type
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
        
        # Simulate priority and channel distribution
        by_priority = {
            "low": total_count // 4,
            "medium": total_count // 2,
            "high": total_count // 4,
            "urgent": max(0, total_count - (total_count // 4) * 3)
        }
        
        by_channel = {
            "in_app": total_count,
            "email": total_count // 2,
            "sms": 0,
            "webhook": 0
        }
        
        return NotificationStats(
            total_notifications=total_count,
            unread_count=unread_count,
            read_count=read_count,
            by_type=by_type,
            by_priority=by_priority,
            by_channel=by_channel,
            delivery_success_rate=95.0,  # Placeholder
            average_read_time=2.5  # 2.5 hours average
        )
    
    async def create_notification_digest(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        digest_type: str = "daily"
    ) -> NotificationDigest:
        """Create notification digest for a user"""
        if digest_type == "daily":
            period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        else:  # weekly
            today = datetime.utcnow().date()
            days_since_monday = today.weekday()
            period_start = datetime.combine(
                today - timedelta(days=days_since_monday),
                datetime.min.time()
            )
            period_end = period_start + timedelta(days=7)
        
        # Get notifications in period
        all_notifications = await notification_repository.get_by_user(
            db, user_id=user_id, limit=1000
        )
        
        period_notifications = [
            n for n in all_notifications
            if period_start <= n.created_at < period_end
        ]
        
        total_count = len(period_notifications)
        
        # Count by type
        by_type = {}
        for notification in period_notifications:
            notification_type = notification.type
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
        
        # Create summary items (top 5 most important)
        summary_items = []
        for notification in sorted(period_notifications, key=lambda x: x.created_at, reverse=True)[:5]:
            summary_items.append({
                "id": str(notification.id),
                "type": notification.type,
                "message": notification.message[:100] + "..." if len(notification.message) > 100 else notification.message,
                "created_at": notification.created_at.isoformat(),
                "is_read": notification.is_read
            })
        
        return NotificationDigest(
            user_id=user_id,
            digest_type=digest_type,
            period_start=period_start,
            period_end=period_end,
            total_notifications=total_count,
            high_priority_count=total_count // 4,  # Placeholder
            urgent_count=max(0, total_count // 10),  # Placeholder
            by_type=by_type,
            summary_items=summary_items
        )
    
    async def cleanup_expired_notifications(
        self,
        db: AsyncSession,
        *,
        days_old: int = 30
    ) -> int:
        """Clean up old read notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Get old read notifications
        all_notifications = await notification_repository.get_multi(db, limit=10000)
        old_read_notifications = [
            n for n in all_notifications
            if n.is_read and n.created_at <= cutoff_date
        ]
        
        # Delete them
        deleted_count = 0
        for notification in old_read_notifications:
            try:
                await notification_repository.remove(db, id=notification.id)
                deleted_count += 1
            except Exception:
                continue
        
        return deleted_count
    
    async def mark_notifications_as_read_by_revision(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        user_id: Optional[UUID] = None
    ) -> int:
        """Mark all notifications related to a revision as read"""
        # Get all notifications for the revision
        all_notifications = await notification_repository.get_multi(db, limit=10000)
        revision_notifications = [
            n for n in all_notifications
            if n.revision_id == revision_id and (user_id is None or n.user_id == user_id)
        ]
        
        marked_count = 0
        for notification in revision_notifications:
            if not notification.is_read:
                try:
                    await notification_repository.mark_as_read(db, notification_id=notification.id)
                    marked_count += 1
                except Exception:
                    continue
        
        return marked_count


# Create singleton instance
notification_service = NotificationService()