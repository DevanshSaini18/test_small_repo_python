from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    """Types of notifications."""
    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_ASSIGNED = "item_assigned"
    ITEM_COMPLETED = "item_completed"
    ITEM_OVERDUE = "item_overdue"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"
    TEAM_ADDED = "team_added"
    SYSTEM = "system"


class NotificationPriority(str, enum.Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """Notification model for user notifications."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Related entities
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    
    # Notification state
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Additional data (JSON string for flexible metadata)
    metadata = Column(Text, nullable=True)
    
    # Action URL (optional link to related resource)
    action_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    # Relationships
    user = relationship("User", backref="notifications")
    item = relationship("Item", backref="notifications")
    comment = relationship("Comment", backref="notifications")


class NotificationPreference(Base):
    """User notification preferences."""
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Email notifications
    email_enabled = Column(Boolean, default=True)
    email_item_assigned = Column(Boolean, default=True)
    email_item_updated = Column(Boolean, default=True)
    email_comment_added = Column(Boolean, default=True)
    email_mention = Column(Boolean, default=True)
    
    # In-app notifications
    inapp_enabled = Column(Boolean, default=True)
    inapp_item_assigned = Column(Boolean, default=True)
    inapp_item_updated = Column(Boolean, default=True)
    inapp_comment_added = Column(Boolean, default=True)
    inapp_mention = Column(Boolean, default=True)
    
    # Digest settings
    daily_digest = Column(Boolean, default=False)
    weekly_digest = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="notification_preferences")
