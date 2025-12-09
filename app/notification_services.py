from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.notification_models import Notification, NotificationPreference, NotificationType, NotificationPriority
from app.notification_schemas import NotificationCreate, NotificationUpdate
from app.models import User, Item, Comment


# ============= Notification Services =============
def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    """Create a new notification."""
    db_notification = Notification(
        title=notification.title,
        message=notification.message,
        type=notification.type,
        priority=notification.priority,
        user_id=notification.user_id,
        item_id=notification.item_id,
        comment_id=notification.comment_id,
        metadata=notification.metadata,
        action_url=notification.action_url,
        expires_at=notification.expires_at
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notification(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Get a notification by ID for a specific user."""
    return db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()


def get_notifications(
    db: Session,
    user_id: int,
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    priority: Optional[NotificationPriority] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Notification]:
    """Get notifications for a user with optional filters."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    if notification_type:
        query = query.filter(Notification.type == notification_type)
    
    if priority:
        query = query.filter(Notification.priority == priority)
    
    # Filter out expired notifications
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    )
    
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Mark a notification as read."""
    notification = get_notification(db, notification_id, user_id)
    if not notification:
        return None
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications as read for a user."""
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    db.commit()
    return count


def mark_bulk_as_read(db: Session, notification_ids: List[int], user_id: int) -> int:
    """Mark multiple notifications as read."""
    count = db.query(Notification).filter(
        Notification.id.in_(notification_ids),
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    }, synchronize_session=False)
    db.commit()
    return count


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """Delete a notification."""
    notification = get_notification(db, notification_id, user_id)
    if not notification:
        return False
    
    db.delete(notification)
    db.commit()
    return True


def delete_all_read_notifications(db: Session, user_id: int) -> int:
    """Delete all read notifications for a user."""
    count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == True
    ).delete()
    db.commit()
    return count


def get_notification_stats(db: Session, user_id: int):
    """Get notification statistics for a user."""
    total = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id
    ).scalar()
    
    unread = db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar()
    
    # By type
    by_type = {}
    for ntype in NotificationType:
        count = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.type == ntype
        ).scalar()
        by_type[ntype.value] = count
    
    # By priority
    by_priority = {}
    for priority in NotificationPriority:
        count = db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.priority == priority
        ).scalar()
        by_priority[priority.value] = count
    
    return {
        "total_notifications": total,
        "unread_count": unread,
        "read_count": total - unread,
        "by_type": by_type,
        "by_priority": by_priority
    }


# ============= Notification Preference Services =============
def get_or_create_preferences(db: Session, user_id: int) -> NotificationPreference:
    """Get or create notification preferences for a user."""
    preferences = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).first()
    
    if not preferences:
        preferences = NotificationPreference(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences


def update_preferences(db: Session, user_id: int, updates: dict) -> NotificationPreference:
    """Update notification preferences for a user."""
    preferences = get_or_create_preferences(db, user_id)
    
    for key, value in updates.items():
        if hasattr(preferences, key):
            setattr(preferences, key, value)
    
    preferences.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preferences)
    return preferences


# ============= Notification Trigger Helpers =============
def notify_item_created(db: Session, item: Item, creator: User):
    """Create notifications when an item is created."""
    # Notify assignees
    for assignee in item.assignees:
        if assignee.id != creator.id:  # Don't notify the creator
            create_notification(db, NotificationCreate(
                title="New Item Assigned",
                message=f"{creator.username} assigned you to: {item.title}",
                type=NotificationType.ITEM_ASSIGNED,
                priority=NotificationPriority.NORMAL if item.priority.value in ["low", "medium"] else NotificationPriority.HIGH,
                user_id=assignee.id,
                item_id=item.id,
                action_url=f"/items/{item.id}"
            ))


def notify_item_updated(db: Session, item: Item, updater: User, changes: dict):
    """Create notifications when an item is updated."""
    # Notify assignees about updates
    for assignee in item.assignees:
        if assignee.id != updater.id:
            # Build change summary
            change_summary = ", ".join([f"{k}" for k in changes.keys()])
            
            create_notification(db, NotificationCreate(
                title="Item Updated",
                message=f"{updater.username} updated {item.title} ({change_summary})",
                type=NotificationType.ITEM_UPDATED,
                priority=NotificationPriority.NORMAL,
                user_id=assignee.id,
                item_id=item.id,
                action_url=f"/items/{item.id}",
                metadata=json.dumps(changes)
            ))
    
    # Notify creator if not an assignee
    if item.created_by_id and item.created_by_id != updater.id:
        if not any(a.id == item.created_by_id for a in item.assignees):
            create_notification(db, NotificationCreate(
                title="Your Item Was Updated",
                message=f"{updater.username} updated your item: {item.title}",
                type=NotificationType.ITEM_UPDATED,
                priority=NotificationPriority.NORMAL,
                user_id=item.created_by_id,
                item_id=item.id,
                action_url=f"/items/{item.id}"
            ))


def notify_item_completed(db: Session, item: Item, completer: User):
    """Create notifications when an item is completed."""
    # Notify creator
    if item.created_by_id and item.created_by_id != completer.id:
        create_notification(db, NotificationCreate(
            title="Item Completed",
            message=f"{completer.username} completed: {item.title}",
            type=NotificationType.ITEM_COMPLETED,
            priority=NotificationPriority.NORMAL,
            user_id=item.created_by_id,
            item_id=item.id,
            action_url=f"/items/{item.id}"
        ))
    
    # Notify other assignees
    for assignee in item.assignees:
        if assignee.id not in [completer.id, item.created_by_id]:
            create_notification(db, NotificationCreate(
                title="Item Completed",
                message=f"{completer.username} completed: {item.title}",
                type=NotificationType.ITEM_COMPLETED,
                priority=NotificationPriority.NORMAL,
                user_id=assignee.id,
                item_id=item.id,
                action_url=f"/items/{item.id}"
            ))


def notify_comment_added(db: Session, comment: Comment, item: Item, author: User):
    """Create notifications when a comment is added."""
    notified_users = set()
    
    # Notify assignees
    for assignee in item.assignees:
        if assignee.id != author.id:
            create_notification(db, NotificationCreate(
                title="New Comment",
                message=f"{author.username} commented on: {item.title}",
                type=NotificationType.COMMENT_ADDED,
                priority=NotificationPriority.NORMAL,
                user_id=assignee.id,
                item_id=item.id,
                comment_id=comment.id,
                action_url=f"/items/{item.id}#comment-{comment.id}"
            ))
            notified_users.add(assignee.id)
    
    # Notify item creator if not already notified
    if item.created_by_id and item.created_by_id != author.id and item.created_by_id not in notified_users:
        create_notification(db, NotificationCreate(
            title="New Comment on Your Item",
            message=f"{author.username} commented on: {item.title}",
            type=NotificationType.COMMENT_ADDED,
            priority=NotificationPriority.NORMAL,
            user_id=item.created_by_id,
            item_id=item.id,
            comment_id=comment.id,
            action_url=f"/items/{item.id}#comment-{comment.id}"
        ))


def check_and_notify_overdue_items(db: Session):
    """Check for overdue items and create notifications."""
    from app.models import ItemStatus
    
    # Get items that are overdue and not completed
    overdue_items = db.query(Item).filter(
        Item.due_date < datetime.utcnow(),
        Item.status != ItemStatus.DONE,
        Item.status != ItemStatus.ARCHIVED
    ).all()
    
    for item in overdue_items:
        # Check if we already sent an overdue notification today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing = db.query(Notification).filter(
            Notification.item_id == item.id,
            Notification.type == NotificationType.ITEM_OVERDUE,
            Notification.created_at >= today_start
        ).first()
        
        if existing:
            continue  # Already notified today
        
        # Notify assignees
        for assignee in item.assignees:
            create_notification(db, NotificationCreate(
                title="Item Overdue",
                message=f"Item is overdue: {item.title}",
                type=NotificationType.ITEM_OVERDUE,
                priority=NotificationPriority.URGENT,
                user_id=assignee.id,
                item_id=item.id,
                action_url=f"/items/{item.id}"
            ))
        
        # Notify creator if not an assignee
        if item.created_by_id and not any(a.id == item.created_by_id for a in item.assignees):
            create_notification(db, NotificationCreate(
                title="Your Item is Overdue",
                message=f"Item is overdue: {item.title}",
                type=NotificationType.ITEM_OVERDUE,
                priority=NotificationPriority.URGENT,
                user_id=item.created_by_id,
                item_id=item.id,
                action_url=f"/items/{item.id}"
            ))
