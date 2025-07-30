"""
Enhanced notification Pydantic schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class NotificationType(str, Enum):
    """Types of notifications"""
    PROPOSAL_SUBMITTED = "proposal_submitted"
    PROPOSAL_APPROVED = "proposal_approved"
    PROPOSAL_REJECTED = "proposal_rejected"
    PROPOSAL_CHANGES_REQUESTED = "proposal_changes_requested"
    PROPOSAL_WITHDRAWN = "proposal_withdrawn"
    APPROVAL_OVERDUE = "approval_overdue"
    APPROVAL_ESCALATED = "approval_escalated"
    SYSTEM_MAINTENANCE = "system_maintenance"
    BULK_OPERATION_COMPLETED = "bulk_operation_completed"


class NotificationPriority(str, Enum):
    """Priority levels for notifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


# Legacy simple notification schemas (for backward compatibility)
class SimpleNotificationBase(BaseModel):
    """Base notification schema"""
    message: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1, max_length=50)


class SimpleNotificationCreate(SimpleNotificationBase):
    """Schema for creating notifications"""
    user_id: uuid.UUID
    revision_id: Optional[uuid.UUID] = None


class SimpleNotification(SimpleNotificationBase):
    """Schema for notification response"""
    id: uuid.UUID
    user_id: uuid.UUID
    revision_id: Optional[uuid.UUID] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Enhanced notification schemas
class NotificationTemplate(BaseModel):
    """Notification template schema"""
    template_id: str
    notification_type: NotificationType
    title_template: str
    message_template: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    variables: List[str]
    is_active: bool = True


class EnhancedNotificationCreate(BaseModel):
    """Schema for creating enhanced notifications"""
    user_id: uuid.UUID
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    data: Optional[Dict[str, Any]] = None
    revision_id: Optional[uuid.UUID] = None
    expires_at: Optional[datetime] = None
    send_immediately: bool = True


class EnhancedNotificationUpdate(BaseModel):
    """Schema for updating enhanced notifications"""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class EnhancedNotificationResponse(BaseModel):
    """Enhanced notification response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[NotificationChannel]
    data: Optional[Dict[str, Any]] = None
    revision_id: Optional[uuid.UUID] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    delivery_status: Dict[str, str] = {}  # channel -> status mapping
    
    class Config:
        from_attributes = True


class NotificationBatch(BaseModel):
    """Schema for batch notification operations"""
    user_ids: List[uuid.UUID] = Field(..., max_items=100)
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    data: Optional[Dict[str, Any]] = None
    send_immediately: bool = True


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: uuid.UUID
    email_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    webhook_url: Optional[str] = None
    quiet_hours_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    notification_types: Dict[str, bool] = {}  # notification_type -> enabled mapping


class NotificationStats(BaseModel):
    """Notification statistics"""
    total_notifications: int
    unread_count: int
    read_count: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    by_channel: Dict[str, int]
    delivery_success_rate: float
    average_read_time: Optional[float] = None  # hours


class NotificationDigest(BaseModel):
    """Daily/weekly notification digest"""
    user_id: uuid.UUID
    digest_type: str  # daily, weekly
    period_start: datetime
    period_end: datetime
    total_notifications: int
    high_priority_count: int
    urgent_count: int
    by_type: Dict[str, int]
    summary_items: List[Dict[str, Any]]


class BulkNotificationResult(BaseModel):
    """Result of bulk notification operation"""
    total_requested: int
    successfully_created: int
    failed_count: int
    failed_users: List[str]
    errors: List[str]
    batch_id: str
    processing_time_ms: int