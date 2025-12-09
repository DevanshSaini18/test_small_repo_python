from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User
from app.notification_models import NotificationType, NotificationPriority
from app.notification_schemas import (
    NotificationCreate, NotificationRead, NotificationUpdate,
    NotificationBulkRead, NotificationStats,
    NotificationPreferenceRead, NotificationPreferenceUpdate
)
from app.notification_services import (
    create_notification, get_notification, get_notifications,
    mark_notification_as_read, mark_all_as_read, mark_bulk_as_read,
    delete_notification, delete_all_read_notifications,
    get_notification_stats,
    get_or_create_preferences, update_preferences
)
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============= Notification Routes =============
@router.post("", response_model=NotificationRead, status_code=status.HTTP_201_CREATED)
def create_new_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new notification (typically used by system/admin).
    Regular users can only create notifications for themselves.
    """
    # Only allow users to create notifications for themselves unless they're admin
    if notification.user_id != current_user.id and current_user.role.value not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create notifications for other users"
        )
    
    return create_notification(db, notification)


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    priority: Optional[NotificationPriority] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user with optional filters."""
    return get_notifications(
        db, 
        current_user.id, 
        is_read=is_read,
        notification_type=notification_type,
        priority=priority,
        skip=skip, 
        limit=limit
    )


@router.get("/unread", response_model=List[NotificationRead])
def list_unread_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unread notifications for the current user."""
    return get_notifications(db, current_user.id, is_read=False, skip=skip, limit=limit)


@router.get("/stats", response_model=NotificationStats)
def get_notification_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for the current user."""
    return get_notification_stats(db, current_user.id)


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification_by_id(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification by ID."""
    notification = get_notification(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = mark_notification_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user."""
    count = mark_all_as_read(db, current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.post("/read-bulk", status_code=status.HTTP_200_OK)
def mark_bulk_notifications_read(
    bulk_read: NotificationBulkRead,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark multiple notifications as read."""
    count = mark_bulk_as_read(db, bulk_read.notification_ids, current_user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_by_id(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a notification."""
    if not delete_notification(db, notification_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return None


@router.delete("/read/all", status_code=status.HTTP_200_OK)
def delete_all_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete all read notifications for the current user."""
    count = delete_all_read_notifications(db, current_user.id)
    return {"message": f"Deleted {count} read notifications"}


# ============= Notification Preference Routes =============
@router.get("/preferences/me", response_model=NotificationPreferenceRead)
def get_my_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for the current user."""
    return get_or_create_preferences(db, current_user.id)


@router.put("/preferences/me", response_model=NotificationPreferenceRead)
def update_my_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences for the current user."""
    updates = preferences.dict(exclude_unset=True)
    return update_preferences(db, current_user.id, updates)
