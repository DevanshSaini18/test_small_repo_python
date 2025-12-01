from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models import PriorityLevel, ItemStatus, UserRole, SubscriptionTier

# ============= Organization Schemas =============
class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    subscription_tier: Optional[SubscriptionTier] = SubscriptionTier.FREE

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    max_users: Optional[int] = None
    max_items: Optional[int] = None

class OrganizationRead(OrganizationBase):
    id: int
    subscription_tier: SubscriptionTier
    max_users: int
    max_items: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# ============= User Schemas =============
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    organization_id: int

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None

class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    organization_id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ============= Team Schemas =============
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TeamRead(TeamBase):
    id: int
    organization_id: int
    created_at: datetime
    members: List[UserRead] = []

    class Config:
        orm_mode = True

# ============= Tag Schemas =============
class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#3B82F6"

class TagCreate(TagBase):
    pass

class TagRead(TagBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ============= Item Schemas =============
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[ItemStatus] = ItemStatus.TODO
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None

class ItemCreate(ItemBase):
    team_id: Optional[int] = None
    parent_item_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ItemStatus] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    team_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None

class ItemRead(ItemBase):
    id: int
    organization_id: int
    team_id: Optional[int] = None
    created_by_id: Optional[int] = None
    parent_item_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    actual_hours: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    assignees: List[UserRead] = []
    tags: List[TagRead] = []

    class Config:
        orm_mode = True

# ============= Comment Schemas =============
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    item_id: int

class CommentUpdate(BaseModel):
    content: str

class CommentRead(CommentBase):
    id: int
    item_id: int
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ============= Attachment Schemas =============
class AttachmentRead(BaseModel):
    id: int
    filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    item_id: int
    uploaded_by_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

# ============= Activity Log Schemas =============
class ActivityLogRead(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

# ============= API Key Schemas =============
class APIKeyCreate(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class APIKeyRead(BaseModel):
    id: int
    key: str
    name: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ============= Webhook Schemas =============
class WebhookBase(BaseModel):
    url: str
    events: str  # Comma-separated

class WebhookCreate(WebhookBase):
    secret: Optional[str] = None

class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[str] = None
    is_active: Optional[bool] = None

class WebhookRead(WebhookBase):
    id: int
    is_active: bool
    organization_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ============= Analytics Schemas =============
class ItemAnalytics(BaseModel):
    total_items: int
    by_status: dict
    by_priority: dict
    overdue_items: int
    completed_this_week: int
    avg_completion_time_hours: Optional[float] = None

class UsageAnalytics(BaseModel):
    total_requests: int
    requests_by_endpoint: dict
    avg_response_time_ms: float
    error_rate: float
