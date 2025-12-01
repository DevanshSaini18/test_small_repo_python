from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

# Association tables for many-to-many relationships
user_teams = Table(
    'user_teams',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE'))
)

item_tags = Table(
    'item_tags',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)

item_assignees = Table(
    'item_assignees',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id', ondelete='CASCADE')),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)

class PriorityLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ItemStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    ARCHIVED = "archived"

class UserRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class SubscriptionTier(enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

# Core Models
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    max_users = Column(Integer, default=5)
    max_items = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="organization", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    teams = relationship("Team", secondary=user_teams, back_populates="members")
    created_items = relationship("Item", foreign_keys="Item.created_by_id", back_populates="creator")
    assigned_items = relationship("Item", secondary=item_assignees, back_populates="assignees")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("User", secondary=user_teams, back_populates="teams")
    items = relationship("Item", back_populates="team")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    color = Column(String, default="#3B82F6")  # Hex color
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("Item", secondary=item_tags, back_populates="tags")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.TODO)
    priority = Column(SQLEnum(PriorityLevel), default=PriorityLevel.MEDIUM)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    
    # Foreign Keys
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    parent_item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="items")
    team = relationship("Team", back_populates="items")
    creator = relationship("User", foreign_keys=[created_by_id], back_populates="created_items")
    assignees = relationship("User", secondary=item_assignees, back_populates="assigned_items")
    tags = relationship("Tag", secondary=item_tags, back_populates="items")
    comments = relationship("Comment", back_populates="item", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="item", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="item", cascade="all, delete-orphan")
    
    # Self-referential for subtasks
    parent_item = relationship("Item", remote_side=[id], backref="subtasks")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("Item", back_populates="attachments")
    uploaded_by = relationship("User")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)  # created, updated, deleted, commented, etc.
    entity_type = Column(String, nullable=False)  # item, comment, user, etc.
    entity_id = Column(Integer)
    details = Column(Text)  # JSON string with change details
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    item = relationship("Item", back_populates="activity_logs")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    events = Column(String, nullable=False)  # Comma-separated: item.created,item.updated
    is_active = Column(Boolean, default=True)
    secret = Column(String)  # For signature verification
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="webhooks")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_logs")
