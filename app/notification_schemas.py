from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.notification_models import NotificationType, NotificationPriority


# ============= Notification Schemas =============
class NotificationBase(BaseModel):
    """Base notification schema."""
    title: str
    message: str
    type: NotificationType
    priority: Optional[NotificationPriority] = NotificationPriority.NORMAL


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: int
    item_id: Optional[int] = None
    comment_id: Optional[int] = None
    metadata: Optional[str] = None
    action_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None


class NotificationRead(NotificationBase):
    """Schema for reading a notification."""
    id: int
    user_id: int
    item_id: Optional[int] = None
    comment_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    metadata: Optional[str] = None
    action_url: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class NotificationBulkRead(BaseModel):
    """Schema for bulk marking notifications as read."""
    notification_ids: List[int] = Field(..., description="List of notification IDs to mark as read")


class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    total_notifications: int
    unread_count: int
    read_count: int
    by_type: dict
    by_priority: dict


# ============= Notification Preference Schemas =============
class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema."""
    email_enabled: Optional[bool] = True
    email_item_assigned: Optional[bool] = True
    email_item_updated: Optional[bool] = True
    email_comment_added: Optional[bool] = True
    email_mention: Optional[bool] = True
    inapp_enabled: Optional[bool] = True
    inapp_item_assigned: Optional[bool] = True
    inapp_item_updated: Optional[bool] = True
    inapp_comment_added: Optional[bool] = True
    inapp_mention: Optional[bool] = True
    daily_digest: Optional[bool] = False
    weekly_digest: Optional[bool] = False


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating notification preferences."""
    user_id: int


class NotificationPreferenceUpdate(NotificationPreferenceBase):
    """Schema for updating notification preferences."""
    pass


class NotificationPreferenceRead(NotificationPreferenceBase):
    """Schema for reading notification preferences."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
